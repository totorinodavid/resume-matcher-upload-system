import os
import sys
import pytest
import pytest_asyncio
import asyncio
import warnings
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text

"""Global pytest fixtures and collection hooks (Neon/Postgres-only).

Tests run strictly against a Postgres/Neon database. Alembic migrations are
applied once per session to ensure schema parity, and each test runs inside a
SAVEPOINT for isolation.
"""

# Do not enable any PostgreSQL fallbacks; backend is Neon/Postgres-only

# Silence recurring pydub ffmpeg presence RuntimeWarning in tests; it's not
# relevant to current backend concerns and creates noise.
warnings.filterwarnings(
    "ignore",
    message="Couldn't find ffmpeg or avconv",
    category=RuntimeWarning,
)

# Ensure parent directory that contains the 'app' package is on PYTHONPATH
_THIS_DIR = os.path.dirname(__file__)
_APP_PARENT = os.path.abspath(os.path.join(_THIS_DIR, '..'))  # -> apps/backend
if _APP_PARENT not in sys.path:
    sys.path.insert(0, _APP_PARENT)

from app.models import Base
from app.core.config import settings as core_settings
from app.core.database import async_engine

# ---------------------------------------------------------------------------
# Test database initialization strategy (Neon/Postgres only)
# ---------------------------------------------------------------------------
def _is_postgres(url: str) -> bool:
    return url.startswith("postgresql+") or url.startswith("postgres://")

ASYNC_DB_URL = os.getenv("ASYNC_DATABASE_URL", "").strip()
SYNC_DB_URL = os.getenv("SYNC_DATABASE_URL", "").strip()
if not (_is_postgres(ASYNC_DB_URL) and _is_postgres(SYNC_DB_URL)):
    raise RuntimeError(
        "Tests require Postgres/Neon. Set SYNC_DATABASE_URL (postgresql+psycopg://) and "
        "ASYNC_DATABASE_URL (postgresql+asyncpg://)."
    )


# Disable background tasks globally for test session to prevent event-loop closed races
os.environ.setdefault("DISABLE_BACKGROUND_TASKS", "true")

@pytest.fixture(scope="session", autouse=True)
def _bg_tasks_disabled_flag():
    os.environ["DISABLE_BACKGROUND_TASKS"] = "true"
    # Ensure auth bypass is NOT globally enabled; specific app factory handles test-time override
    if os.environ.get("DISABLE_AUTH_FOR_TESTS") == "1":
        os.environ.pop("DISABLE_AUTH_FOR_TESTS", None)
    yield


@pytest.fixture(scope="session", autouse=True)
def _ensure_async_engine_disposed():
    """Ensure the global async_engine is disposed at end of test session.

    Helps ensure proper cleanup of PostgreSQL connections while event loop
    is still alive.
    """
    yield
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():  # pragma: no cover - defensive
            return
        loop.run_until_complete(async_engine.dispose())
    except RuntimeError:
        # If no running loop / already closed, ignore.
        pass


@pytest.fixture(scope="session", autouse=True)
def _apply_alembic_migrations_once():
    """Run Alembic migrations to head once for the test session."""
    from alembic import command
    from alembic.config import Config as AlembicConfig

    ini_path = os.path.abspath(os.path.join(_APP_PARENT, 'alembic.ini'))
    cfg = AlembicConfig(ini_path)
    # Force URL directly (avoids relying on env interpolation)
    cfg.set_main_option("sqlalchemy.url", SYNC_DB_URL)
    # Ensure script_location resolves to the backend's alembic folder even when CWD is repo root
    cfg.set_main_option("script_location", os.path.abspath(os.path.join(_APP_PARENT, 'alembic')))
    command.upgrade(cfg, "head")


@pytest_asyncio.fixture()
async def db_session():
    """Return an isolated AsyncSession for unit tests.

    For Postgres we connect to the real test database (already migrated) and
    wrap each test in a SAVEPOINT (nested transaction) for isolation. For
    PostgreSQL in-memory we just create a fresh engine per test.
    """
    engine = create_async_engine(ASYNC_DB_URL, future=True)
    async with engine.connect() as conn:
        trans = await conn.begin()
        SessionLocal = async_sessionmaker(bind=conn, expire_on_commit=False, class_=AsyncSession)
        async with SessionLocal() as session:
            try:
                yield session
            finally:
                await session.rollback()
        await trans.rollback()
    await engine.dispose()


# ---------------------------------------------------------------------------
# Credits system test helpers and fixtures
# ---------------------------------------------------------------------------

from uuid import uuid4


@pytest_asyncio.fixture
async def db_conn():
    """
    Provide isolated database connection with transaction rollback.
    
    Each test runs in its own transaction that gets rolled back,
    ensuring no persistent changes to the database.
    """
    engine = create_async_engine(ASYNC_DB_URL, future=True)
    async with engine.connect() as conn:
        # Start transaction
        trans = await conn.begin()
        try:
            yield conn
        finally:
            # Always rollback to ensure isolation
            await trans.rollback()
    await engine.dispose()


# Helper functions for test data creation

async def insert_user(
    conn, 
    email: str = None, 
    name: str = None, 
    start_balance: int = 0
) -> str:
    """Insert a test user and return the user ID."""
    user_id = str(uuid4())
    email = email or f"test-{uuid4()}@example.com"
    name = name or f"Test User {uuid4().hex[:8]}"
    
    result = await conn.execute(
        text("""
            INSERT INTO users (id, email, name, credits_balance)
            VALUES (:user_id, :email, :name, :credits_balance)
            RETURNING id
        """),
        {
            "user_id": user_id,
            "email": email,
            "name": name,
            "credits_balance": start_balance
        }
    )
    
    returned_id = result.scalar_one()
    assert returned_id == user_id
    return user_id


async def insert_payment(
    conn,
    user_id: str,
    intent_id: str = None,
    amount_cents: int = 500,
    expected_credits: int = 100,
    status: str = "PAID",
    provider: str = "stripe",
    currency: str = "EUR"
) -> str:
    """Insert a test payment and return the payment ID."""
    payment_id = str(uuid4())
    intent_id = intent_id or f"pi_test_{uuid4().hex[:16]}"
    
    result = await conn.execute(
        text("""
            INSERT INTO payments (
                id, user_id, provider, provider_payment_intent_id,
                amount_total_cents, currency, expected_credits, 
                status, raw_provider_data
            )
            VALUES (
                :payment_id, :user_id, :provider, :intent_id,
                :amount_cents, :currency, :expected_credits,
                :status, '{}'::jsonb
            )
            RETURNING id
        """),
        {
            "payment_id": payment_id,
            "user_id": user_id,
            "provider": provider,
            "intent_id": intent_id,
            "amount_cents": amount_cents,
            "currency": currency,
            "expected_credits": expected_credits,
            "status": status
        }
    )
    
    returned_id = result.scalar_one()
    assert returned_id == payment_id
    return payment_id


async def apply_credit_purchase(
    conn,
    user_id: str,
    payment_id: str,
    delta_credits: int,
    reason: str = "PURCHASE"
) -> tuple[str, int]:
    """
    Apply credit purchase: create transaction and update user balance.
    
    Returns (transaction_id, new_balance).
    """
    # Insert credit transaction
    tx_id = str(uuid4())
    await conn.execute(
        text("""
            INSERT INTO credit_transactions (
                id, user_id, payment_id, delta_credits, reason, meta
            )
            VALUES (:tx_id, :user_id, :payment_id, :delta_credits, :reason, '{}'::jsonb)
        """),
        {
            "tx_id": tx_id,
            "user_id": user_id,
            "payment_id": payment_id,
            "delta_credits": delta_credits,
            "reason": reason
        }
    )
    
    # Update user balance and return new balance
    result = await conn.execute(
        text("""
            UPDATE users 
            SET credits_balance = credits_balance + :delta_credits 
            WHERE id = :user_id
            RETURNING credits_balance
        """),
        {"delta_credits": delta_credits, "user_id": user_id}
    )
    
    new_balance = result.scalar_one()
    return tx_id, new_balance


async def get_user_balance(conn, user_id: str) -> int:
    """Get current user credit balance."""
    result = await conn.execute(
        text("SELECT credits_balance FROM users WHERE id = :user_id"),
        {"user_id": user_id}
    )
    return result.scalar_one()


async def count_credit_transactions(conn, user_id: str = None, payment_id: str = None) -> int:
    """Count credit transactions with optional filters."""
    query = "SELECT COUNT(*) FROM credit_transactions WHERE 1=1"
    params = {}
    
    if user_id:
        query += " AND user_id = :user_id"
        params["user_id"] = user_id
        
    if payment_id:
        query += " AND payment_id = :payment_id"
        params["payment_id"] = payment_id
        
    result = await conn.execute(text(query), params)
    return result.scalar_one()


async def payment_exists_by_intent(conn, provider: str, intent_id: str) -> bool:
    """Check if payment exists by provider and intent ID."""
    result = await conn.execute(
        text("""
            SELECT COUNT(*) FROM payments 
            WHERE provider = :provider AND provider_payment_intent_id = :intent_id
        """),
        {"provider": provider, "intent_id": intent_id}
    )
    return result.scalar_one() > 0


def pytest_collection_modifyitems(config, items):  # type: ignore
    """Filter out parametrized trio variants generated by anyio if present.

    Some prior collection state may have added [trio] variants before our
    markers; drop them to avoid ModuleNotFoundError when trio isn't installed.
    """
    filtered = []
    for item in items:
        if item.name.endswith("[trio]"):
            continue
        filtered.append(item)
    items[:] = filtered
