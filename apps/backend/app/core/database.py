from __future__ import annotations

from functools import lru_cache
from typing import AsyncGenerator, Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import QueuePool, NullPool

from .config import settings as app_settings
from ..models.base import Base


class _DatabaseSettings:
    """PostgreSQL-only database configuration - no SQLite support."""

    SYNC_DATABASE_URL: str = app_settings.SYNC_DATABASE_URL
    ASYNC_DATABASE_URL: str = app_settings.ASYNC_DATABASE_URL
    DB_ECHO: bool = app_settings.DB_ECHO
    DB_POOL_SIZE: Optional[int] = app_settings.DB_POOL_SIZE
    DB_MAX_OVERFLOW: Optional[int] = app_settings.DB_MAX_OVERFLOW
    DB_POOL_TIMEOUT: Optional[int] = app_settings.DB_POOL_TIMEOUT

    # PostgreSQL-specific connection arguments
    DB_CONNECT_ARGS = {
        "sslmode": "prefer",
        "connect_timeout": 10,
        "command_timeout": 30,
    }


settings = _DatabaseSettings()


@lru_cache(maxsize=1)
def _make_sync_engine() -> Engine:
    """Create PostgreSQL-only synchronous Engine for Neon Local Connect.
    
    Always uses postgresql+psycopg:// scheme for consistent behavior.
    NO SQLite fallbacks - PostgreSQL is required for ALL environments.
    """
    sync_url: str = settings.SYNC_DATABASE_URL
    
    # Enforce PostgreSQL with psycopg driver - NO SQLite allowed!
    if not sync_url.startswith('postgresql+psycopg://'):
        if sync_url.startswith('postgres://'):
            # Convert postgres:// to postgresql+psycopg://
            sync_url = sync_url.replace('postgres://', 'postgresql+psycopg://', 1)
        elif sync_url.startswith('postgresql://'):
            # Convert postgresql:// to postgresql+psycopg://
            sync_url = sync_url.replace('postgresql://', 'postgresql+psycopg://', 1)
        else:
            raise RuntimeError(
                f"ONLY PostgreSQL is supported! Got: {sync_url}. "
                "Use Neon Local Connect: postgresql+psycopg://postgres:password@localhost:5432/dbname"
            )
    
    create_kwargs = {
        "echo": settings.DB_ECHO,
        "pool_pre_ping": True,
        "poolclass": QueuePool,
        "connect_args": settings.DB_CONNECT_ARGS,
        "future": True,
    }
    
    # PostgreSQL connection pooling
    if settings.DB_POOL_SIZE is not None:
        create_kwargs["pool_size"] = settings.DB_POOL_SIZE
    if settings.DB_MAX_OVERFLOW is not None:
        create_kwargs["max_overflow"] = settings.DB_MAX_OVERFLOW
    if settings.DB_POOL_TIMEOUT is not None:
        create_kwargs["pool_timeout"] = settings.DB_POOL_TIMEOUT
    
    engine = create_engine(sync_url, **create_kwargs)
    return engine


@lru_cache(maxsize=1)
def _make_async_engine() -> AsyncEngine:
    """Create PostgreSQL-only asynchronous Engine for Neon Local Connect.
    
    Always uses postgresql+asyncpg:// scheme for consistent behavior.
    No SQLite fallbacks - PostgreSQL is required for all environments.
    """
    async_url: str = settings.ASYNC_DATABASE_URL
    
    # Enforce PostgreSQL with asyncpg driver
    if not async_url.startswith('postgresql+asyncpg://'):
        if async_url.startswith('postgres://'):
            # Convert postgres:// to postgresql+asyncpg://
            async_url = async_url.replace('postgres://', 'postgresql+asyncpg://', 1)
        elif async_url.startswith('postgresql://'):
            # Convert postgresql:// to postgresql+asyncpg://
            async_url = async_url.replace('postgresql://', 'postgresql+asyncpg://', 1)
        else:
            raise RuntimeError(
                f"Invalid database URL: {async_url}. "
                "Only PostgreSQL is supported. Use format: postgresql+asyncpg://user:pass@localhost:5432/dbname"
            )
    
    create_kwargs = {
        "echo": settings.DB_ECHO,
        "pool_pre_ping": True,
        "poolclass": NullPool,  # Use NullPool for asyncio compatibility
        "connect_args": {},  # asyncpg handles SSL and timeouts differently
        "future": True,
    }
    
    # Note: NullPool doesn't support pool_size, max_overflow, pool_timeout
    # These settings are ignored when using NullPool for development/testing
    
    engine = create_async_engine(async_url, **create_kwargs)
    return engine


# ──────────────────────────────────────────────────────────────────────────────
# Session factories
# ──────────────────────────────────────────────────────────────────────────────

sync_engine: Engine = _make_sync_engine()
async_engine: AsyncEngine = _make_async_engine()

SessionLocal: sessionmaker[Session] = sessionmaker(
    bind=sync_engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)

AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
)


def get_sync_db_session() -> Generator[Session, None, None]:
    """
    Yield a *transactional* synchronous ``Session``.

    Commits if no exception was raised, otherwise rolls back. Always closes.
    Useful for CLI scripts or rare sync paths.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            try:
                await session.commit()
            except Exception:
                # Ensure the transaction is not left in a broken state
                try:
                    await session.rollback()
                except Exception:
                    pass
                raise
        except Exception:
            try:
                await session.rollback()
            except Exception:
                pass
            raise


async def init_models(Base: Base) -> None:
    """Create tables for provided Base metadata using PostgreSQL."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def get_engine_sync() -> Engine:
    """Return the configured synchronous engine.

    Provided for auxiliary scripts (schema drift detection) that need a bound
    Engine without importing the async stack or constructing duplicate engines.
    """
    return sync_engine
