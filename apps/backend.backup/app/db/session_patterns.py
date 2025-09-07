# ------------------------------------------------------------------
# 3) PYTHON: Sichere Session/Transaktions-Patterns (SQLAlchemy async)
# ------------------------------------------------------------------
# Wichtig: Nach JEDEM DB-Fehler rollback(), sonst bleibt die Session im Fehlerzustand.
# Benutze dieses Pattern überall in deinen Services/Handlern.

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Callable, Any, TypeVar
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')

async def run_in_tx(async_session_factory: Callable, work_coro: Callable[[AsyncSession], Any]) -> Any:
    """
    Execute work within a database transaction with proper error handling.
    
    Features:
    - Automatic rollback on any SQLAlchemyError
    - Proper transaction management with begin()
    - Comprehensive error logging
    - Type-safe return value
    
    Args:
        async_session_factory: Factory function that creates AsyncSession
        work_coro: Coroutine function that performs work with the session
        
    Returns:
        Result from work_coro execution
        
    Raises:
        SQLAlchemyError: Re-raised after rollback
    """
    async with async_session_factory() as session:
        try:
            async with session.begin():
                logger.debug("Starting database transaction")
                result = await work_coro(session)
                logger.debug("Transaction completed successfully")
                return result
        except SQLAlchemyError as e:
            logger.error(f"Database transaction failed: {e}", exc_info=True)
            await session.rollback()
            raise
        except Exception as e:
            logger.error(f"Non-database error in transaction: {e}", exc_info=True)
            await session.rollback()
            raise


async def safe_commit(session: AsyncSession) -> bool:
    """
    Safely commit a session with automatic rollback on failure.
    
    Args:
        session: Active AsyncSession
        
    Returns:
        True if commit succeeded, False if it failed
    """
    try:
        await session.commit()
        logger.debug("Session committed successfully")
        return True
    except SQLAlchemyError as e:
        logger.error(f"Commit failed, rolling back: {e}", exc_info=True)
        try:
            await session.rollback()
        except Exception as rollback_error:
            logger.error(f"Rollback also failed: {rollback_error}", exc_info=True)
        return False


async def safe_rollback(session: AsyncSession) -> bool:
    """
    Safely rollback a session with error handling.
    
    Args:
        session: Active AsyncSession
        
    Returns:
        True if rollback succeeded, False if it failed
    """
    try:
        await session.rollback()
        logger.debug("Session rolled back successfully")
        return True
    except Exception as e:
        logger.error(f"Rollback failed: {e}", exc_info=True)
        return False
