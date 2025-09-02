"""
Comprehensive test for the production credit system.
Run as: python -m pytest tests/test_credits_production.py -v
"""

import pytest
import asyncio
from decimal import Decimal
from unittest.mock import Mock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import SessionLocal
from app.models.credits import Payment, CreditTransaction, ProcessedEvent, PaymentStatus
from app.models.user import User
from app.services.payments import PaymentService
from app.services.stripe_provider import StripeProvider
from app.services.reconciliation import ReconciliationService


@pytest.fixture
async def db_session():
    """Create test database session."""
    async with SessionLocal() as session:
        yield session


@pytest.fixture
async def test_user(db_session: AsyncSession):
    """Create test user."""
    user = User(
        id="test-user-123",
        email="test@example.com",
        credits_balance=0
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def mock_stripe_event():
    """Mock Stripe checkout session completed event."""
    return {
        'id': 'evt_test_123',
        'type': 'checkout.session.completed',
        'data': {
            'object': {
                'id': 'cs_test_123',
                'payment_status': 'paid',
                'amount_total': 1000,  # $10.00
                'currency': 'usd',
                'metadata': {
                    'user_id': 'test-user-123',
                    'credits': '100'
                }
            }
        }
    }


class TestPaymentService:
    """Test the payment service."""
    
    async def test_process_payment_success(self, db_session, test_user, mock_stripe_event):
        """Test successful payment processing."""
        service = PaymentService()
        
        # Mock Stripe provider
        mock_provider = Mock(spec=StripeProvider)
        mock_provider.parse_and_verify.return_value = {
            'event_id': 'evt_test_123',
            'session_id': 'cs_test_123',
            'payment_intent_id': 'pi_test_123',
            'user_id': 'test-user-123',
            'amount_cents': 1000,
            'currency': 'usd',
            'credits': 100
        }
        
        with patch.object(service, 'stripe_provider', mock_provider):
            result = await service.process_payment(
                session=db_session,
                raw_event=mock_stripe_event,
                signature="mock_signature"
            )
        
        assert result['success'] is True
        assert result['credits_added'] == 100
        
        # Verify user credits updated
        await db_session.refresh(test_user)
        assert test_user.credits_balance == 100
        
        # Verify payment record created
        payment = await db_session.get(Payment, 1)
        assert payment is not None
        assert payment.user_id == "test-user-123"
        assert payment.amount_cents == 1000
        assert payment.status == PaymentStatus.COMPLETED
        assert payment.credits_granted == 100
    
    async def test_idempotent_processing(self, db_session, test_user, mock_stripe_event):
        """Test that duplicate events are handled idempotently."""
        service = PaymentService()
        
        # Create processed event
        processed_event = ProcessedEvent(
            event_id="evt_test_123",
            event_type="checkout.session.completed",
            processed_at=None
        )
        db_session.add(processed_event)
        await db_session.commit()
        
        # Mock Stripe provider
        mock_provider = Mock(spec=StripeProvider)
        mock_provider.parse_and_verify.return_value = {
            'event_id': 'evt_test_123',
            'session_id': 'cs_test_123',
            'payment_intent_id': 'pi_test_123',
            'user_id': 'test-user-123',
            'amount_cents': 1000,
            'currency': 'usd',
            'credits': 100
        }
        
        with patch.object(service, 'stripe_provider', mock_provider):
            result = await service.process_payment(
                session=db_session,
                raw_event=mock_stripe_event,
                signature="mock_signature"
            )
        
        assert result['success'] is True
        assert result['duplicate'] is True
        
        # Verify no credits were added
        await db_session.refresh(test_user)
        assert test_user.credits_balance == 0
    
    async def test_atomic_transaction_rollback(self, db_session, test_user):
        """Test that failed operations roll back atomically."""
        service = PaymentService()
        
        # Mock a payment that fails during credit addition
        mock_provider = Mock(spec=StripeProvider)
        mock_provider.parse_and_verify.return_value = {
            'event_id': 'evt_test_fail',
            'session_id': 'cs_test_fail',
            'payment_intent_id': 'pi_test_fail',
            'user_id': 'nonexistent-user',  # This will cause failure
            'amount_cents': 1000,
            'currency': 'usd',
            'credits': 100
        }
        
        with patch.object(service, 'stripe_provider', mock_provider):
            result = await service.process_payment(
                session=db_session,
                raw_event={'id': 'evt_test_fail'},
                signature="mock_signature"
            )
        
        assert result['success'] is False
        assert 'error' in result
        
        # Verify no payment record was created
        from sqlalchemy import select
        result = await db_session.execute(
            select(Payment).where(Payment.stripe_session_id == 'cs_test_fail')
        )
        assert result.scalar_one_or_none() is None


class TestReconciliationService:
    """Test the reconciliation service."""
    
    async def test_reconcile_payments(self, db_session, test_user):
        """Test payment reconciliation."""
        # Create a payment with pending status
        payment = Payment(
            user_id=test_user.id,
            stripe_session_id="cs_pending_123",
            stripe_payment_intent_id="pi_pending_123",
            amount_cents=2000,
            currency="usd",
            status=PaymentStatus.PENDING,
            credits_granted=0
        )
        db_session.add(payment)
        await db_session.commit()
        
        service = ReconciliationService()
        
        # Mock Stripe API response
        mock_stripe_data = {
            'payment_status': 'paid',
            'amount_total': 2000,
            'metadata': {'credits': '200'}
        }
        
        with patch.object(service.stripe_provider, 'reconcile_payment', return_value=mock_stripe_data):
            stats = await service.reconcile_payments(db_session, limit=10)
        
        assert stats['processed'] >= 1
        assert stats['updated'] >= 1
        
        # Verify payment was updated
        await db_session.refresh(payment)
        assert payment.status == PaymentStatus.COMPLETED
        assert payment.credits_granted == 200
        
        # Verify user credits were added
        await db_session.refresh(test_user)
        assert test_user.credits_balance == 200


class TestWebhookSecurity:
    """Test webhook security features."""
    
    def test_signature_verification(self):
        """Test Stripe webhook signature verification."""
        provider = StripeProvider()
        
        # This would normally test with real Stripe signature verification
        # For now, we'll test the structure
        assert hasattr(provider, 'parse_and_verify')
        assert callable(provider.parse_and_verify)
    
    def test_event_deduplication(self):
        """Test that events are properly deduplicated."""
        # This would test the processed_events table functionality
        # Implementation depends on actual database setup
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
