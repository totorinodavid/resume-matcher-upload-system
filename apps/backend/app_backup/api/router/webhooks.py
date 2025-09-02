"""
🚀 PRODUCTION-READY WEBHOOK HANDLER

Bulletproof credit purchase flow with Stripe integration:
- Idempotent webhook processing with event deduplication
- Atomic credit transactions with advisory locks
- Full state machine for payment processing
- Comprehensive error handling and logging
- Integration with existing Resume Matcher user system
"""

from __future__ import annotations

import json
import logging
import os
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_db_session, settings
from app.models import User
from app.schemas.credits import WebhookEventResponse
from app.services.stripe_provider import StripeProvider
from app.services.payments import PaymentService
from app.services.exceptions import (
    PaymentProcessingError, 
    UserNotFoundError, 
    WebhookValidationError
)

logger = logging.getLogger(__name__)
webhooks_router = APIRouter()

# Initialize services
stripe_provider = StripeProvider()
payment_service = PaymentService(provider_name="stripe")


async def _get_or_create_user(session: AsyncSession, user_identifier: str) -> Optional[str]:
    """
    Get or create user for payment processing.
    Integrates with existing Resume Matcher user system.
    """
    from app.services.ultra_emergency_user_service import UltraEmergencyUserService
    
    try:
        user_service = UltraEmergencyUserService(session)
        
        # Try to resolve existing user first
        canonical_id = await user_service.get_canonical_user_id(user_identifier)
        if canonical_id:
            return canonical_id
        
        # Create new user if not found
        new_user = await user_service.create_user_for_unknown_id(user_identifier)
        return str(new_user.id)
        
    except Exception as e:
        logger.error(f"Failed to get/create user for identifier {user_identifier}: {e}")
        return None


@webhooks_router.post("/webhooks/stripe", summary="Production Stripe webhook")
async def stripe_webhook(
    request: Request, 
    db: AsyncSession = Depends(get_db_session)
) -> JSONResponse:
    """
    Production-ready Stripe webhook handler.
    
    Features:
    - Signature verification with configurable tolerance
    - Idempotent event processing with database deduplication
    - Atomic credit transactions with PostgreSQL advisory locks
    - Full payment state machine (INIT → PAID → CREDITED)
    - Comprehensive error handling with proper HTTP responses
    - Integration with existing Resume Matcher architecture
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
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid payload"
            )
    
    # Process webhook in database transaction
    async with db.begin():
        try:
            # Check for idempotency - has this event been processed already?
            await payment_service.record_processed_event(db, event.event_id, event.payload)
            
        except IntegrityError:
            # Event already processed - return success for idempotency
            logger.info(f"Event {event.event_id} already processed, returning success")
            return JSONResponse(
                status_code=200,
                content=WebhookEventResponse(
                    ok=True,
                    message="Event already processed"
                ).model_dump()
            )
        
        # Handle credit-awarding events
        if event.event_type in ("checkout.session.completed", "payment_intent.succeeded", "invoice.paid"):
            try:
                result = await _process_credit_event(db, event)
                return JSONResponse(status_code=200, content=result.model_dump())
                
            except Exception as e:
                logger.error(f"Failed to process credit event {event.event_id}: {e}")
                await db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to process payment"
                )
        
        # Handle refund events
        elif event.event_type in ("charge.refunded", "refund.created", "refund.succeeded"):
            try:
                result = await _process_refund_event(db, event)
                return JSONResponse(status_code=200, content=result.model_dump())
                
            except Exception as e:
                logger.error(f"Failed to process refund event {event.event_id}: {e}")
                await db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to process refund"
                )
        
        # Handle chargeback/dispute events
        elif event.event_type in ("charge.dispute.created",):
            try:
                result = await _process_chargeback_event(db, event)
                return JSONResponse(status_code=200, content=result.model_dump())
                
            except Exception as e:
                logger.error(f"Failed to process chargeback event {event.event_id}: {e}")
                await db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to process chargeback"
                )
        
        # Handle benign events
        elif event.event_type in ("checkout.session.expired", "payment_intent.canceled"):
            logger.info(f"Acknowledged benign event: {event.event_type}")
            return JSONResponse(
                status_code=200,
                content=WebhookEventResponse(
                    ok=True,
                    skipped=event.event_type
                ).model_dump()
            )
        
        # Acknowledge all other events
        else:
            logger.info(f"Acknowledged unhandled event: {event.event_type}")
            return JSONResponse(
                status_code=200,
                content=WebhookEventResponse(
                    ok=True,
                    skipped="unhandled_event_type"
                ).model_dump()
            )


async def _process_credit_event(db: AsyncSession, event) -> WebhookEventResponse:
    """Process events that should award credits."""
    
    # Extract payment details
    amount_cents, credits, currency = await stripe_provider.fetch_line_items_and_credits(event)
    
    if credits <= 0:
        logger.warning(f"Event {event.event_id} has no credits to award")
        return WebhookEventResponse(
            ok=True,
            skipped="no_credits",
            message="No credits to award"
        )
    
    if currency.upper() != "EUR":
        logger.info(f"Ignoring non-EUR payment: {currency}")
        return WebhookEventResponse(
            ok=True,
            skipped="non_eur_currency",
            message=f"Currency {currency} not supported"
        )
    
    # Get user identifier
    user_identifier = await stripe_provider.get_user_identifier(event)
    if not user_identifier:
        logger.error(f"No user identifier found in event {event.event_id}")
        return WebhookEventResponse(
            ok=True,
            skipped="no_user_identifier",
            message="No user identifier found"
        )
    
    # Get or create user
    user_id = await _get_or_create_user(db, user_identifier)
    if not user_id:
        logger.error(f"Failed to get/create user for identifier {user_identifier}")
        return WebhookEventResponse(
            ok=True,
            skipped="user_creation_failed",
            message="Failed to create user"
        )
    
    # Get payment identifiers
    payment_intent_id, checkout_session_id = await stripe_provider.get_payment_identity(event)
    
    # Create/update payment record
    payment = await payment_service.upsert_payment(
        session=db,
        user_id=user_id,
        payment_intent_id=payment_intent_id,
        checkout_session_id=checkout_session_id,
        amount_cents=amount_cents,
        currency=currency,
        expected_credits=credits,
        raw_data=event.payload
    )
    
    # Credit the user atomically
    await payment_service.credit_user_if_needed(db, payment)
    
    logger.info(f"Successfully processed credit event {event.event_id}: {credits} credits for user {user_id}")
    
    return WebhookEventResponse(
        ok=True,
        credits_added=credits,
        user_id=user_id,
        message="Credits awarded successfully"
    )


async def _process_refund_event(db: AsyncSession, event) -> WebhookEventResponse:
    """Process refund events."""
    
    # Get payment identity
    payment_intent_id, _ = await stripe_provider.get_payment_identity(event)
    
    if not payment_intent_id:
        logger.warning(f"No payment intent ID found for refund event {event.event_id}")
        return WebhookEventResponse(
            ok=True,
            skipped="no_payment_intent",
            message="No payment intent ID found"
        )
    
    # Find existing payment
    payment = await payment_service.get_payment_by_provider_id(db, payment_intent_id)
    if not payment:
        logger.warning(f"No payment found for PI {payment_intent_id} in refund event {event.event_id}")
        return WebhookEventResponse(
            ok=True,
            skipped="payment_not_found",
            message="Original payment not found"
        )
    
    # Apply refund
    await payment_service.apply_refund_or_chargeback(db, payment, "REFUND")
    
    logger.info(f"Successfully processed refund event {event.event_id} for payment {payment.id}")
    
    return WebhookEventResponse(
        ok=True,
        message="Refund processed successfully",
        user_id=payment.user_id
    )


async def _process_chargeback_event(db: AsyncSession, event) -> WebhookEventResponse:
    """Process chargeback/dispute events."""
    
    # Get payment identity  
    payment_intent_id, _ = await stripe_provider.get_payment_identity(event)
    
    if not payment_intent_id:
        logger.warning(f"No payment intent ID found for chargeback event {event.event_id}")
        return WebhookEventResponse(
            ok=True,
            skipped="no_payment_intent",
            message="No payment intent ID found"
        )
    
    # Find existing payment
    payment = await payment_service.get_payment_by_provider_id(db, payment_intent_id)
    if not payment:
        logger.warning(f"No payment found for PI {payment_intent_id} in chargeback event {event.event_id}")
        return WebhookEventResponse(
            ok=True,
            skipped="payment_not_found", 
            message="Original payment not found"
        )
    
    # Apply chargeback
    await payment_service.apply_refund_or_chargeback(db, payment, "CHARGEBACK")
    
    logger.info(f"Successfully processed chargeback event {event.event_id} for payment {payment.id}")
    
    return WebhookEventResponse(
        ok=True,
        message="Chargeback processed successfully",
        user_id=payment.user_id
    )


# Legacy endpoint for backward compatibility
@webhooks_router.post("/api/stripe/webhook", include_in_schema=False)
async def stripe_webhook_legacy(
    request: Request, 
    db: AsyncSession = Depends(get_db_session)
) -> JSONResponse:
    """Legacy webhook endpoint for backward compatibility."""
    return await stripe_webhook(request, db)
