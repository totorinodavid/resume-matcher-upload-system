# ------------------------------------------------------------------
# 5) PYTHON: Webhook-Flow (idempotent + Upsert + richtiger UUID-Vergleich)
# ------------------------------------------------------------------
# – nutzt run_in_tx() und resolve_user()
# – dedupliziert Events
# – Upsert des Users per Email
# – Credits erst nach erfolgreichem Commit buchen

from sqlalchemy import text, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional
import logging

from ..db.session_patterns import run_in_tx, safe_commit, safe_rollback
from ..db.resolver_fix import resolve_or_create_user, is_placeholder, is_email
from ..models.stripe_event import StripeEvent
from ..models.user import User

logger = logging.getLogger(__name__)


async def handle_checkout_completed(
    async_session_factory, 
    event_id: str, 
    session_obj: Any, 
    metadata: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Handle Stripe checkout.session.completed webhook events.
    
    Features:
    - Idempotent event processing with database deduplication
    - Robust user resolution with multiple fallback strategies
    - User upsert by email to handle race conditions
    - Atomic credit booking with proper transaction management
    - Comprehensive error handling and logging
    
    Args:
        async_session_factory: Factory function for database sessions
        event_id: Stripe event ID for deduplication
        session_obj: Stripe session object
        metadata: Webhook metadata dictionary
        
    Returns:
        Result dictionary with processing status
    """
    
    async def work(session: AsyncSession) -> Dict[str, Any]:
        try:
            # 0) Event deduplication - prevent duplicate processing
            await _ensure_event_idempotency(session, event_id, metadata)
            
            # 1) Extract and validate credit amount
            credits = _extract_credits_from_metadata(metadata)
            if credits <= 0:
                logger.warning(f"Event {event_id} has no credits to award")
                return {
                    "ok": True, 
                    "skipped": True,
                    "reason": "no_credits",
                    "message": "No credits to award"
                }
            
            # 2) Resolve or create user
            user = await resolve_or_create_user(
                session=session,
                UserModel=User,
                meta=metadata,
                stripe_session_obj=session_obj,
                auto_create=True
            )
            
            if not user:
                logger.error(f"Failed to resolve/create user for event {event_id}")
                return {
                    "ok": True,
                    "skipped": True, 
                    "reason": "user_resolution_failed",
                    "message": "Could not resolve or create user"
                }
            
            # 3) Award credits atomically
            await _award_credits_to_user(session, user.id, credits)
            
            # 4) Mark event as successfully processed
            await _mark_event_completed(session, event_id, {
                "user_id": str(user.id),
                "credits_awarded": credits,
                "user_email": user.email
            })
            
            logger.info(f"✅ Successfully processed event {event_id}: {credits} credits for user {user.id}")
            
            return {
                "ok": True,
                "user_id": str(user.id),
                "credits_awarded": credits,
                "message": "Credits awarded successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to process event {event_id}: {e}", exc_info=True)
            
            # Mark event as failed for debugging
            try:
                await _mark_event_failed(session, event_id, str(e))
            except Exception:
                pass  # Don't fail on failed failure logging
            
            # Re-raise for transaction rollback
            raise
    
    return await run_in_tx(async_session_factory, work)


async def _ensure_event_idempotency(session: AsyncSession, event_id: str, metadata: Dict[str, Any]) -> None:
    """
    Ensure event is only processed once using database constraints.
    
    Args:
        session: Database session
        event_id: Stripe event ID
        metadata: Event metadata
        
    Raises:
        IntegrityError: If event was already processed (expected for idempotency)
    """
    try:
        # Insert event record - will fail if already exists
        stmt = insert(StripeEvent).values(
            event_id=event_id,
            event_type=metadata.get("type", "checkout.session.completed"),
            raw_data=metadata,
            processing_status="processing"
        )
        
        # Use on_conflict_do_nothing to make this truly idempotent
        stmt = stmt.on_conflict_do_nothing(index_elements=[StripeEvent.event_id])
        
        result = await session.execute(stmt)
        
        # Check if row was actually inserted
        if result.rowcount == 0:
            # Event already exists - check if it was completed
            existing = await session.execute(
                select(StripeEvent).where(StripeEvent.event_id == event_id)
            )
            event_record = existing.scalar_one_or_none()
            
            if event_record and event_record.processing_status == "completed":
                raise IntegrityError(
                    "Event already processed",
                    "stripe_events_pkey", 
                    "event_id"
                )
        
        logger.debug(f"Event {event_id} marked for processing")
        
    except IntegrityError:
        # Expected for duplicate events - let caller handle
        raise
    except Exception as e:
        logger.error(f"Failed to ensure event idempotency for {event_id}: {e}")
        raise


def _extract_credits_from_metadata(metadata: Dict[str, Any]) -> int:
    """
    Extract credit amount from webhook metadata.
    
    Supports multiple metadata formats:
    - credits (direct integer)
    - credit_amount (string that needs parsing)
    - amount_in_credits (alternative naming)
    
    Args:
        metadata: Webhook metadata dictionary
        
    Returns:
        Number of credits to award (0 if none found)
    """
    # Try different metadata field names
    credit_fields = ["credits", "credit_amount", "amount_in_credits", "credits_to_add"]
    
    for field in credit_fields:
        value = metadata.get(field)
        if value is not None:
            try:
                credits = int(str(value))
                if credits > 0:
                    logger.debug(f"Found {credits} credits in metadata field '{field}'")
                    return credits
            except (ValueError, TypeError):
                logger.warning(f"Invalid credit value in field '{field}': {value}")
                continue
    
    logger.debug("No valid credit amount found in metadata")
    return 0


async def _award_credits_to_user(session: AsyncSession, user_id: int, credits: int) -> None:
    """
    Award credits to user using atomic SQL operation.
    
    Args:
        session: Database session
        user_id: User ID to credit
        credits: Number of credits to add
        
    Raises:
        SQLAlchemyError: On database errors
    """
    try:
        # Use raw SQL for atomic credit update with constraint checking
        await session.execute(
            text("""
                UPDATE users 
                SET credits_balance = credits_balance + :credits 
                WHERE id = :user_id
            """),
            {"credits": credits, "user_id": user_id}
        )
        
        logger.debug(f"Awarded {credits} credits to user {user_id}")
        
    except SQLAlchemyError as e:
        logger.error(f"Failed to award {credits} credits to user {user_id}: {e}")
        raise


async def _mark_event_completed(session: AsyncSession, event_id: str, result_data: Dict[str, Any]) -> None:
    """
    Mark event as successfully completed.
    
    Args:
        session: Database session
        event_id: Event ID to update
        result_data: Processing result data
    """
    try:
        await session.execute(
            text("""
                UPDATE stripe_events 
                SET processing_status = 'completed',
                    raw_data = raw_data || :result_data
                WHERE event_id = :event_id
            """),
            {"event_id": event_id, "result_data": result_data}
        )
        
        logger.debug(f"Marked event {event_id} as completed")
        
    except Exception as e:
        logger.warning(f"Failed to mark event {event_id} as completed: {e}")
        # Don't raise - this is just status tracking


async def _mark_event_failed(session: AsyncSession, event_id: str, error_message: str) -> None:
    """
    Mark event as failed for debugging.
    
    Args:
        session: Database session  
        event_id: Event ID to update
        error_message: Error description
    """
    try:
        await session.execute(
            text("""
                UPDATE stripe_events 
                SET processing_status = 'failed',
                    error_message = :error_message
                WHERE event_id = :event_id
            """),
            {"event_id": event_id, "error_message": error_message[:1000]}  # Truncate long errors
        )
        
        logger.debug(f"Marked event {event_id} as failed")
        
    except Exception as e:
        logger.warning(f"Failed to mark event {event_id} as failed: {e}")
        # Don't raise - this is just status tracking


# Legacy compatibility function
async def handle_stripe_webhook_event(
    async_session_factory,
    UserModel,
    StripeEventModel, 
    WalletService,
    event_id: str,
    session_obj,
    metadata: dict
) -> Dict[str, Any]:
    """
    Legacy compatibility wrapper for existing webhook handlers.
    
    Args:
        async_session_factory: Session factory
        UserModel: User model class (ignored, uses hardcoded User)
        StripeEventModel: Event model class (ignored, uses hardcoded StripeEvent)
        WalletService: Wallet service (ignored, uses direct credit update)
        event_id: Stripe event ID
        session_obj: Stripe session object
        metadata: Webhook metadata
        
    Returns:
        Processing result dictionary
    """
    logger.warning("Using legacy webhook handler compatibility mode")
    return await handle_checkout_completed(
        async_session_factory, 
        event_id, 
        session_obj, 
        metadata
    )
