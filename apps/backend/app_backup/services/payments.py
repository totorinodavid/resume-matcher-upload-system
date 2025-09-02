"""
Production-ready payment service with full state machine
Handles idempotent credit processing with advisory locks
"""

from __future__ import annotations

import hashlib
import json
import logging
from typing import Optional, Dict, Any

from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Payment, User, CreditTransaction, ProcessedEvent, PaymentStatus
from app.services.exceptions import PaymentProcessingError, UserNotFoundError

logger = logging.getLogger(__name__)


class PaymentService:
    """Production-ready payment processing service."""
    
    def __init__(self, provider_name: str):
        self.provider = provider_name

    async def _advisory_lock(self, session: AsyncSession, key: str) -> None:
        """Acquire PostgreSQL advisory lock for the transaction."""
        try:
            await session.execute(
                text("SELECT pg_advisory_xact_lock(hashtext(:key))")
                .bindparams(key=key)
            )
        except Exception as e:
            logger.error(f"Failed to acquire advisory lock for key {key}: {e}")
            raise PaymentProcessingError(f"Failed to acquire lock: {e}") from e

    async def record_processed_event(self, session: AsyncSession, event_id: str, payload: Dict[str, Any]) -> None:
        """Record processed event for idempotency checking."""
        try:
            payload_sha = hashlib.sha256(
                json.dumps(payload, sort_keys=True).encode()
            ).hexdigest()
            
            processed_event = ProcessedEvent(
                provider=self.provider,
                provider_event_id=event_id,
                payload_sha256=payload_sha
            )
            
            session.add(processed_event)
            await session.flush()  # Will raise IntegrityError for duplicates
            
        except IntegrityError:
            # Event already processed - this is expected for idempotency
            raise
        except Exception as e:
            logger.error(f"Failed to record processed event {event_id}: {e}")
            raise PaymentProcessingError(f"Failed to record event: {e}") from e

    async def upsert_payment(
        self,
        session: AsyncSession,
        user_id: str,
        payment_intent_id: Optional[str],
        checkout_session_id: Optional[str],
        amount_cents: int,
        currency: str,
        expected_credits: int,
        raw_data: Dict[str, Any]
    ) -> Payment:
        """Create or update payment record."""
        try:
            # Try to find existing payment by PI or CS
            stmt = select(Payment).where(
                Payment.provider == self.provider,
                (Payment.provider_payment_intent_id == payment_intent_id) |
                (Payment.provider_checkout_session_id == checkout_session_id)
            ).with_for_update(of=Payment)
            
            result = await session.execute(stmt)
            payment = result.scalar_one_or_none()
            
            if not payment:
                # Create new payment
                payment = Payment(
                    user_id=user_id,
                    provider=self.provider,
                    provider_payment_intent_id=payment_intent_id,
                    provider_checkout_session_id=checkout_session_id,
                    amount_total_cents=amount_cents,
                    currency=currency,
                    expected_credits=expected_credits,
                    status=PaymentStatus.PAID,
                    raw_provider_data=raw_data
                )
                session.add(payment)
                await session.flush()
                logger.info(f"Created new payment {payment.id} for user {user_id}")
            else:
                # Update existing payment
                payment.amount_total_cents = amount_cents or payment.amount_total_cents
                payment.currency = currency or payment.currency
                
                if expected_credits:
                    payment.expected_credits = expected_credits
                
                if payment_intent_id and not payment.provider_payment_intent_id:
                    payment.provider_payment_intent_id = payment_intent_id
                    
                if checkout_session_id and not payment.provider_checkout_session_id:
                    payment.provider_checkout_session_id = checkout_session_id
                
                # Update status if it was in a temporary state
                if payment.status in (PaymentStatus.INIT, PaymentStatus.FAILED, PaymentStatus.CANCELED):
                    payment.status = PaymentStatus.PAID
                
                payment.raw_provider_data = raw_data
                await session.flush()
                logger.info(f"Updated payment {payment.id} for user {user_id}")
            
            return payment
            
        except Exception as e:
            logger.error(f"Failed to upsert payment for user {user_id}: {e}")
            raise PaymentProcessingError(f"Failed to upsert payment: {e}") from e

    async def credit_user_if_needed(self, session: AsyncSession, payment: Payment) -> None:
        """Atomically credit user if payment hasn't been credited yet."""
        if payment.status == PaymentStatus.CREDITED:
            logger.info(f"Payment {payment.id} already credited, skipping")
            return
        
        if payment.expected_credits <= 0:
            logger.warning(f"Payment {payment.id} has no credits to award")
            return
        
        try:
            # Acquire advisory lock
            lock_key = payment.provider_payment_intent_id or payment.provider_checkout_session_id or str(payment.id)
            await self._advisory_lock(session, lock_key)
            
            # Atomically update user credits
            delta = int(payment.expected_credits)
            result = await session.execute(
                text("""
                    UPDATE users 
                    SET credits_balance = credits_balance + :delta 
                    WHERE id = :user_id 
                    RETURNING credits_balance
                """).bindparams(delta=delta, user_id=payment.user_id)
            )
            
            new_balance = result.scalar_one_or_none()
            if new_balance is None:
                raise UserNotFoundError(f"User {payment.user_id} not found")
            
            # Create audit trail
            credit_transaction = CreditTransaction(
                user_id=payment.user_id,
                payment_id=payment.id,
                delta_credits=delta,
                reason="PURCHASE",
                meta={
                    "provider": self.provider,
                    "payment_intent_id": payment.provider_payment_intent_id,
                    "checkout_session_id": payment.provider_checkout_session_id
                }
            )
            session.add(credit_transaction)
            
            # Mark payment as credited
            payment.status = PaymentStatus.CREDITED
            await session.flush()
            
            logger.info(
                f"Successfully credited user {payment.user_id} with {delta} credits. "
                f"New balance: {new_balance}"
            )
            
        except Exception as e:
            logger.error(f"Failed to credit user for payment {payment.id}: {e}")
            raise PaymentProcessingError(f"Failed to credit user: {e}") from e

    async def apply_refund_or_chargeback(
        self, 
        session: AsyncSession, 
        payment: Payment, 
        reason: str
    ) -> None:
        """Apply negative credit transaction for refunds/chargebacks."""
        try:
            # Acquire advisory lock
            lock_key = payment.provider_payment_intent_id or str(payment.id)
            await self._advisory_lock(session, lock_key)
            
            # Apply negative delta
            delta = -int(payment.expected_credits)
            result = await session.execute(
                text("""
                    UPDATE users 
                    SET credits_balance = credits_balance + :delta 
                    WHERE id = :user_id 
                    RETURNING credits_balance
                """).bindparams(delta=delta, user_id=payment.user_id)
            )
            
            new_balance = result.scalar_one_or_none()
            if new_balance is None:
                raise UserNotFoundError(f"User {payment.user_id} not found")
            
            # Create negative audit trail
            credit_transaction = CreditTransaction(
                user_id=payment.user_id,
                payment_id=payment.id,
                delta_credits=delta,
                reason=reason,
                meta={
                    "provider": self.provider,
                    "original_credits": payment.expected_credits
                }
            )
            session.add(credit_transaction)
            
            # Update payment status
            payment.status = PaymentStatus.REFUNDED if reason == "REFUND" else PaymentStatus.CHARGEBACK
            await session.flush()
            
            logger.info(
                f"Applied {reason} for payment {payment.id}: {delta} credits. "
                f"New balance: {new_balance}"
            )
            
        except Exception as e:
            logger.error(f"Failed to apply {reason} for payment {payment.id}: {e}")
            raise PaymentProcessingError(f"Failed to apply {reason}: {e}") from e

    async def get_payment_by_provider_id(
        self, 
        session: AsyncSession, 
        provider_payment_intent_id: str
    ) -> Optional[Payment]:
        """Get payment by provider payment intent ID."""
        try:
            stmt = select(Payment).where(
                Payment.provider == self.provider,
                Payment.provider_payment_intent_id == provider_payment_intent_id
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get payment by provider ID {provider_payment_intent_id}: {e}")
            return None

    async def get_payments_for_reconciliation(
        self, 
        session: AsyncSession, 
        limit: int = 200
    ) -> list[Payment]:
        """Get payments that need reconciliation."""
        try:
            stmt = select(Payment).where(
                Payment.provider == self.provider,
                Payment.status.in_([PaymentStatus.INIT, PaymentStatus.PAID])
            ).order_by(Payment.created_at.asc()).limit(limit)
            
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Failed to get payments for reconciliation: {e}")
            return []
