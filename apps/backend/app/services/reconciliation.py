"""
Production-ready reconciliation service
Daily reconciliation of payments with Stripe
"""

from __future__ import annotations

import logging
from typing import Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

from app.models import Payment, PaymentStatus
from app.services.payments import PaymentService
from app.services.stripe_provider import StripeProvider
from app.services.exceptions import PaymentProcessingError

logger = logging.getLogger(__name__)


class ReconciliationService:
    """Service for reconciling payments with external providers."""
    
    def __init__(self):
        self.stripe_provider = StripeProvider()
        self.payment_service = PaymentService(provider_name="stripe")

    async def reconcile_payments(
        self, 
        session: AsyncSession, 
        limit: int = 200
    ) -> Dict[str, int]:
        """
        Reconcile payments with Stripe.
        Returns statistics about the reconciliation process.
        """
        stats = {
            "processed": 0,
            "credited": 0,
            "canceled": 0,
            "refunded": 0,
            "failed": 0,
            "errors": 0
        }
        
        try:
            # Get payments that need reconciliation
            payments = await self.payment_service.get_payments_for_reconciliation(session, limit)
            
            for payment in payments:
                try:
                    await self._reconcile_single_payment(session, payment, stats)
                    stats["processed"] += 1
                except Exception as e:
                    logger.error(f"Failed to reconcile payment {payment.id}: {e}")
                    stats["errors"] += 1
                    continue
            
            await session.commit()
            logger.info(f"Reconciliation complete: {stats}")
            return stats
            
        except Exception as e:
            await session.rollback()
            logger.error(f"Reconciliation failed: {e}")
            raise PaymentProcessingError(f"Reconciliation failed: {e}") from e

    async def _reconcile_single_payment(
        self, 
        session: AsyncSession, 
        payment: Payment, 
        stats: Dict[str, int]
    ) -> None:
        """Reconcile a single payment with Stripe."""
        if not payment.provider_payment_intent_id:
            logger.warning(f"Payment {payment.id} has no payment intent ID, skipping")
            return
        
        try:
            # Acquire lock for this payment
            lock_key = payment.provider_payment_intent_id
            await self.payment_service._advisory_lock(session, lock_key)
            
            # Fetch current status from Stripe
            stripe_data = await self.stripe_provider.reconcile_payment(
                payment.provider_payment_intent_id
            )
            
            stripe_status = stripe_data.get("status")
            charges = stripe_data.get("charges", {}).get("data", [])
            amount = stripe_data.get("amount", 0)
            currency = stripe_data.get("currency", "").upper()
            
            # Refresh payment from database with lock
            refreshed_payment = await session.get(
                Payment, 
                payment.id, 
                with_for_update={"of": [Payment]}
            )
            if not refreshed_payment:
                logger.warning(f"Payment {payment.id} not found during reconciliation")
                return
            
            # Update basic payment details
            refreshed_payment.amount_total_cents = amount
            refreshed_payment.currency = currency
            refreshed_payment.raw_provider_data = stripe_data
            
            # Handle successful payments
            if stripe_status == "succeeded":
                if refreshed_payment.status != PaymentStatus.CREDITED:
                    refreshed_payment.status = PaymentStatus.PAID
                    await session.flush()
                    await self.payment_service.credit_user_if_needed(session, refreshed_payment)
                    stats["credited"] += 1
                    logger.info(f"Reconciled successful payment {payment.id}")
            
            # Handle canceled/failed payments
            elif stripe_status in ("canceled", "requires_payment_method"):
                if refreshed_payment.status not in (PaymentStatus.CANCELED, PaymentStatus.FAILED):
                    refreshed_payment.status = PaymentStatus.CANCELED
                    stats["canceled"] += 1
                    logger.info(f"Marked payment {payment.id} as canceled")
            
            # Handle refunds
            refunded = any(charge.get("refunded", False) for charge in charges)
            if refunded and refreshed_payment.status != PaymentStatus.REFUNDED:
                await self.payment_service.apply_refund_or_chargeback(
                    session, refreshed_payment, "REFUND"
                )
                stats["refunded"] += 1
                logger.info(f"Applied refund to payment {payment.id}")
            
            # Handle disputes/chargebacks
            disputed = any(bool(charge.get("dispute")) for charge in charges)
            if disputed and refreshed_payment.status != PaymentStatus.CHARGEBACK:
                await self.payment_service.apply_refund_or_chargeback(
                    session, refreshed_payment, "CHARGEBACK"
                )
                stats["refunded"] += 1  # Count as refunded for stats
                logger.info(f"Applied chargeback to payment {payment.id}")
            
            await session.flush()
            
        except Exception as e:
            logger.error(f"Failed to reconcile payment {payment.id}: {e}")
            raise

    async def get_reconciliation_metrics(self, session: AsyncSession) -> Dict[str, Any]:
        """Get metrics for reconciliation monitoring."""
        try:
            # Count payments by status
            result = await session.execute(
                text("""
                    SELECT 
                        status,
                        COUNT(*) as count,
                        SUM(amount_total_cents) as total_amount_cents,
                        SUM(expected_credits) as total_credits
                    FROM payments 
                    WHERE provider = 'stripe'
                    GROUP BY status
                """)
            )
            
            status_stats = {}
            for row in result:
                status_stats[row.status] = {
                    "count": row.count,
                    "total_amount_cents": row.total_amount_cents or 0,
                    "total_credits": row.total_credits or 0
                }
            
            # Count payments needing reconciliation
            pending_result = await session.execute(
                text("""
                    SELECT COUNT(*) as count
                    FROM payments 
                    WHERE provider = 'stripe' 
                    AND status IN ('INIT', 'PAID')
                    AND created_at < NOW() - INTERVAL '1 hour'
                """)
            )
            pending_count = pending_result.scalar_one()
            
            # Count recent processed events
            events_result = await session.execute(
                text("""
                    SELECT COUNT(*) as count
                    FROM processed_events 
                    WHERE provider = 'stripe'
                    AND received_at > NOW() - INTERVAL '24 hours'
                """)
            )
            recent_events = events_result.scalar_one()
            
            return {
                "status_breakdown": status_stats,
                "pending_reconciliation": pending_count,
                "recent_webhook_events": recent_events,
                "timestamp": "now()"
            }
            
        except Exception as e:
            logger.error(f"Failed to get reconciliation metrics: {e}")
            raise PaymentProcessingError(f"Failed to get metrics: {e}") from e
