"""
🚀 HOTFIX: Bulletproof Webhook Handler with Enhanced User Resolution

Integrates the comprehensive hotfix for:
- Secure transaction patterns with automatic rollback
- Robust user resolution (Email/UUID/Integer ID support)  
- Idempotent event processing with database deduplication
- Direct credits_balance column updates (production-ready)
- Enhanced error handling and logging
"""

from __future__ import annotations

import json
import logging
import os
from typing import Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_db_session, settings
from app.models import User
from app.models.stripe_event import StripeEvent
from app.schemas.credits import WebhookEventResponse
from app.services.stripe_provider import StripeProvider
from app.services.exceptions import (
    PaymentProcessingError, 
    UserNotFoundError, 
    WebhookValidationError
)

# Import hotfix components
from app.db.session_patterns import run_in_tx, safe_commit, safe_rollback
from app.db.resolver_fix import resolve_or_create_user, is_placeholder, is_email
from app.webhooks.stripe_checkout_completed_hotfix import handle_checkout_completed

logger = logging.getLogger(__name__)
webhooks_hotfix_router = APIRouter()

# Initialize services
stripe_provider = StripeProvider()


@webhooks_hotfix_router.post("/webhooks/stripe/hotfix", summary="Bulletproof Stripe webhook with hotfix")
async def stripe_webhook_hotfix(
    request: Request, 
    db: AsyncSession = Depends(get_db_session)
) -> JSONResponse:
    """
    Bulletproof Stripe webhook handler with comprehensive hotfix.
    
    Features:
    - ✅ Secure transaction patterns with automatic rollback
    - ✅ Robust user resolution (Email/UUID/Integer ID/Placeholder detection)
    - ✅ Idempotent event processing with database deduplication  
    - ✅ Direct credits_balance updates (bypasses complex payment system)
    - ✅ User upsert by email to handle race conditions
    - ✅ Enhanced error handling and comprehensive logging
    - ✅ Signature verification with E2E test mode support
    - ✅ Multiple fallback strategies for user identification
    
    Hotfix Components:
    - session_patterns.py: Safe transaction management with rollback
    - resolver_fix.py: Smart user resolution with multiple ID types
    - stripe_checkout_completed_hotfix.py: Atomic credit processing
    """
    
    # Validate configuration
    if not settings.STRIPE_WEBHOOK_SECRET:
        logger.error("Stripe webhook secret not configured")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Webhook not configured"
        )
    
    # Get request data
    payload = await request.body()
    signature_header = request.headers.get("stripe-signature")
    
    if not signature_header:
        logger.warning("Missing Stripe signature header")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing signature"
        )
    
    # Parse and verify webhook
    try:
        event = await stripe_provider.parse_and_verify(payload, signature_header)
        logger.info(f"✅ Verified Stripe event: {event.event_id} ({event.event_type})")
    except Exception as e:
        # Allow E2E test mode to bypass signature verification
        e2e_mode = os.getenv('E2E_TEST_MODE', '').strip().lower() in ('1', 'true')
        if not e2e_mode:
            logger.warning(f"Webhook signature verification failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid signature"
            )
        
        # E2E mode: parse raw JSON
        try:
            raw_event = json.loads(payload.decode('utf-8'))
            from app.services.payment_provider import PaymentEvent
            event = PaymentEvent(
                provider="stripe",
                event_type=raw_event["type"],
                event_id=raw_event["id"],
                payload=raw_event
            )
            logger.info(f"🧪 E2E mode: Processing event {event.event_id} ({event.event_type})")
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid payload"
            )
    
    # Route to appropriate hotfix handler
    if event.event_type == "checkout.session.completed":
        return await _handle_checkout_completed_hotfix(db, event)
    elif event.event_type in ("payment_intent.succeeded", "invoice.paid"):
        return await _handle_payment_succeeded_hotfix(db, event)
    elif event.event_type in ("charge.refunded", "refund.created", "refund.succeeded"):
        return await _handle_refund_hotfix(db, event)
    elif event.event_type in ("charge.dispute.created",):
        return await _handle_chargeback_hotfix(db, event)
    elif event.event_type in ("checkout.session.expired", "payment_intent.canceled"):
        return await _acknowledge_benign_event(db, event)
    else:
        return await _acknowledge_unknown_event(db, event)


async def _handle_checkout_completed_hotfix(db: AsyncSession, event) -> JSONResponse:
    """Handle checkout.session.completed with hotfix patterns."""
    
    async def work(session: AsyncSession) -> Dict[str, Any]:
        # Extract session object and metadata
        session_obj = event.payload.get("data", {}).get("object", {})
        metadata = session_obj.get("metadata", {})
        
        logger.info(f"Processing checkout completion for event {event.event_id}")
        logger.debug(f"Session metadata: {metadata}")
        
        # Use hotfix handler
        result = await handle_checkout_completed(
            async_session_factory=lambda: session,  # Use current session
            event_id=event.event_id,
            session_obj=session_obj,
            metadata=metadata
        )
        
        return result
    
    try:
        # Use session factory pattern from hotfix
        async def session_factory():
            return db
        
        result = await run_in_tx(session_factory, work)
        
        return JSONResponse(
            status_code=200,
            content=WebhookEventResponse(
                ok=True,
                credits_added=result.get("credits_awarded", 0),
                user_id=result.get("user_id"),
                message=result.get("message", "Credits awarded successfully")
            ).model_dump()
        )
        
    except IntegrityError as e:
        if "stripe_events_pkey" in str(e) or "event_id" in str(e):
            # Event already processed - idempotent response
            logger.info(f"Event {event.event_id} already processed (idempotent)")
            return JSONResponse(
                status_code=200,
                content=WebhookEventResponse(
                    ok=True,
                    message="Event already processed"
                ).model_dump()
            )
        else:
            logger.error(f"Database integrity error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database integrity error"
            )
    
    except Exception as e:
        logger.error(f"Failed to process checkout completion {event.event_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process payment"
        )


async def _handle_payment_succeeded_hotfix(db: AsyncSession, event) -> JSONResponse:
    """Handle payment_intent.succeeded with hotfix patterns."""
    
    # Extract payment intent and metadata
    payment_intent = event.payload.get("data", {}).get("object", {})
    metadata = payment_intent.get("metadata", {})
    
    logger.info(f"Processing payment success for event {event.event_id}")
    
    # Convert to checkout session format for compatibility
    session_obj = {
        "id": payment_intent.get("id"),
        "metadata": metadata,
        "customer_details": {
            "email": metadata.get("customer_email")
        }
    }
    
    try:
        async def session_factory():
            return db
        
        result = await handle_checkout_completed(
            async_session_factory=session_factory,
            event_id=event.event_id,
            session_obj=session_obj,
            metadata=metadata
        )
        
        return JSONResponse(
            status_code=200,
            content=WebhookEventResponse(
                ok=True,
                credits_added=result.get("credits_awarded", 0),
                user_id=result.get("user_id"),
                message=result.get("message", "Payment processed successfully")
            ).model_dump()
        )
        
    except Exception as e:
        logger.error(f"Failed to process payment success {event.event_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process payment"
        )


async def _handle_refund_hotfix(db: AsyncSession, event) -> JSONResponse:
    """Handle refunds with hotfix patterns."""
    
    logger.info(f"Processing refund for event {event.event_id}")
    
    # For now, just acknowledge refund events
    # TODO: Implement credit deduction logic
    return JSONResponse(
        status_code=200,
        content=WebhookEventResponse(
            ok=True,
            skipped="refund_not_implemented",
            message="Refund acknowledged but not processed"
        ).model_dump()
    )


async def _handle_chargeback_hotfix(db: AsyncSession, event) -> JSONResponse:
    """Handle chargebacks with hotfix patterns."""
    
    logger.info(f"Processing chargeback for event {event.event_id}")
    
    # For now, just acknowledge chargeback events  
    # TODO: Implement credit deduction logic
    return JSONResponse(
        status_code=200,
        content=WebhookEventResponse(
            ok=True,
            skipped="chargeback_not_implemented", 
            message="Chargeback acknowledged but not processed"
        ).model_dump()
    )


async def _acknowledge_benign_event(db: AsyncSession, event) -> JSONResponse:
    """Acknowledge benign events that don't require processing."""
    
    logger.info(f"Acknowledging benign event: {event.event_type}")
    
    return JSONResponse(
        status_code=200,
        content=WebhookEventResponse(
            ok=True,
            skipped=event.event_type,
            message=f"Acknowledged benign event: {event.event_type}"
        ).model_dump()
    )


async def _acknowledge_unknown_event(db: AsyncSession, event) -> JSONResponse:
    """Acknowledge unknown events."""
    
    logger.info(f"Acknowledging unknown event: {event.event_type}")
    
    return JSONResponse(
        status_code=200,
        content=WebhookEventResponse(
            ok=True,
            skipped="unhandled_event_type",
            message=f"Acknowledged unhandled event: {event.event_type}"
        ).model_dump()
    )


# Legacy compatibility endpoint  
@webhooks_hotfix_router.post("/api/stripe/webhook/hotfix", include_in_schema=False)
async def stripe_webhook_hotfix_legacy(
    request: Request, 
    db: AsyncSession = Depends(get_db_session)
) -> JSONResponse:
    """Legacy webhook endpoint with hotfix for backward compatibility."""
    return await stripe_webhook_hotfix(request, db)
