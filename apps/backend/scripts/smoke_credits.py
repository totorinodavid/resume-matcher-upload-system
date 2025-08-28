from __future__ import annotations

"""
Minimal smoke test for credits flow using an ephemeral SQLite database.

This bypasses the full pytest suite and Postgres requirements by:
- Creating a temporary SQLite database
- Creating tables from models
- Using CreditsService to credit and read balance

Exit code 0 on success, non-zero on failure.
"""

import asyncio
import os
import sys
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import event
from datetime import datetime, timezone

# Ensure 'app' package is importable when running this script directly
_HERE = os.path.dirname(__file__)
_APP_DIR = os.path.abspath(os.path.join(_HERE, os.pardir))
if _APP_DIR not in sys.path:
    sys.path.insert(0, _APP_DIR)

from app.models import Base
from app.services.credits_service import CreditsService


async def main() -> int:
    # Use in-memory sqlite with aiosqlite
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    # Register a UDF 'now' so server_default text("now()") in models works under SQLite
    @event.listens_for(engine.sync_engine, "connect")
    def _register_now(dbapi_connection, connection_record):  # type: ignore[no-redef]
        try:
            dbapi_connection.create_function("now", 0, lambda: datetime.now(timezone.utc).isoformat())
        except Exception:
            pass
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            # Recreate credit_ledger with AUTOINCREMENT for SQLite
            await conn.exec_driver_sql("DROP TABLE IF EXISTS credit_ledger")
            await conn.exec_driver_sql(
                """
                CREATE TABLE credit_ledger (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  clerk_user_id TEXT NOT NULL REFERENCES stripe_customers(clerk_user_id) ON DELETE RESTRICT,
                  delta INTEGER NOT NULL,
                  reason TEXT NOT NULL,
                  stripe_event_id TEXT,
                  created_at TEXT NOT NULL DEFAULT (now())
                )
                """
            )

        SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
        async with SessionLocal() as session:
            svc = CreditsService(session)
            user = "smoke-user"
            await svc.ensure_customer(clerk_user_id=user)
            bal0 = await svc.get_balance(clerk_user_id=user)
            if bal0 != 0:
                print(f"FAIL: expected initial balance 0, got {bal0}")
                return 2
            await svc.credit_purchase(clerk_user_id=user, delta=50, reason="smoke", stripe_event_id="evt_smoke")
            await session.commit()
            bal1 = await svc.get_balance(clerk_user_id=user)
            if bal1 != 50:
                print(f"FAIL: expected balance 50 after credit, got {bal1}")
                return 3
            print("OK: balance increased to 50 after credit")

            return 0
    finally:
        await engine.dispose()


if __name__ == "__main__":
    code = asyncio.run(main())
    sys.exit(code)
