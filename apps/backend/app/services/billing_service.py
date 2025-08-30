"""
Billing Service für sichere Stripe-Operationen
Alle Stripe Secret-Operations werden hier durchgeführt
"""
import logging
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings

logger = logging.getLogger(__name__)


class BillingService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self._stripe = None
    
    async def _get_stripe(self):
        """Lazy loading für Stripe Client"""
        if self._stripe is None:
            if not settings.STRIPE_SECRET_KEY:
                raise ValueError("STRIPE_SECRET_KEY not configured")
            
            # Import nur wenn benötigt
            try:
                from stripe import Stripe
                self._stripe = Stripe(
                    api_key=settings.STRIPE_SECRET_KEY,
                    api_version='2024-12-18'  # type: ignore
                )
                logger.debug("Stripe client initialized successfully")
            except ImportError as e:
                raise ImportError("Stripe package not available. Install with: pip install stripe") from e
        
        return self._stripe
    
    async def create_billing_portal_session(
        self, 
        user_id: str,
        return_url: str = None
    ) -> Dict[str, Any]:
        """
        Erstellt eine sichere Stripe Billing Portal Session
        
        Args:
            user_id: Eindeutige User-ID (von NextAuth/Auth)
            return_url: URL nach Portal-Beendigung
            
        Returns:
            Dict mit portal_url und session_info
            
        Raises:
            ValueError: Bei ungültigen Parametern
            RuntimeError: Bei Stripe-API-Fehlern
        """
        if not user_id:
            raise ValueError("user_id is required")
        
        stripe = await self._get_stripe()
        
        try:
            # 1. Prüfe ob Customer bereits existiert
            customer_id = await self._get_or_create_stripe_customer(user_id)
            
            # 2. Erstelle Portal Session
            portal_session = await stripe.billing_portal.sessions.create_async({
                'customer': customer_id,
                'return_url': return_url or f"{settings.FRONTEND_URL}/billing"
            })
            
            logger.info(f"Billing portal session created for user_id={user_id} customer_id={customer_id}")
            
            return {
                'portal_url': portal_session.url,
                'session_id': portal_session.id,
                'customer_id': customer_id
            }
            
        except Exception as e:
            logger.error(f"Failed to create billing portal session for user_id={user_id}: {e}")
            raise RuntimeError(f"Failed to create billing portal: {str(e)}") from e
    
    async def _get_or_create_stripe_customer(self, user_id: str) -> str:
        """
        Holt bestehenden Stripe Customer oder erstellt neuen
        
        Args:
            user_id: Eindeutige User-ID
            
        Returns:
            Stripe Customer ID
        """
        # Import hier um zirkuläre Abhängigkeiten zu vermeiden
        from app.models import StripeCustomer
        from sqlalchemy import select
        
        stripe = await self._get_stripe()
        
        # 1. Prüfe lokale Mapping-Tabelle
        result = await self.db.execute(
            select(StripeCustomer).where(StripeCustomer.user_id == user_id)
        )
        existing = result.scalar_one_or_none()
        
        if existing and existing.stripe_customer_id:
            logger.debug(f"Found existing Stripe customer for user_id={user_id}")
            return existing.stripe_customer_id
        
        # 2. Erstelle neuen Stripe Customer
        try:
            customer = await stripe.customers.create_async({
                'metadata': {
                    'user_id': user_id,
                    'source': 'resume_matcher_billing_service'
                }
            })
            
            # 3. Speichere Mapping in DB
            if existing:
                # Update existing record
                existing.stripe_customer_id = customer.id
            else:
                # Create new record
                new_customer = StripeCustomer(
                    user_id=user_id,
                    stripe_customer_id=customer.id
                )
                self.db.add(new_customer)
            
            await self.db.commit()
            
            logger.info(f"Created new Stripe customer for user_id={user_id} customer_id={customer.id}")
            return customer.id
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to create Stripe customer for user_id={user_id}: {e}")
            raise RuntimeError(f"Failed to create customer: {str(e)}") from e
    
    async def create_checkout_session(
        self,
        user_id: str,
        price_id: str,
        success_url: str = None,
        cancel_url: str = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Erstellt eine sichere Stripe Checkout Session
        
        Args:
            user_id: User-ID für Zuordnung
            price_id: Stripe Price ID für gewünschtes Produkt
            success_url: URL nach erfolgreichem Checkout
            cancel_url: URL bei Checkout-Abbruch
            metadata: Zusätzliche Metadaten
            
        Returns:
            Dict mit checkout_url und session_info
        """
        stripe = await self._get_stripe()
        
        try:
            checkout_metadata = {
                'user_id': user_id,
                'source': 'resume_matcher_billing_service'
            }
            if metadata:
                checkout_metadata.update(metadata)
            
            session = await stripe.checkout.sessions.create_async({
                'payment_method_types': ['card'],
                'line_items': [{
                    'price': price_id,
                    'quantity': 1,
                }],
                'mode': 'payment',  # oder 'subscription' je nach Bedarf
                'success_url': success_url or f"{settings.FRONTEND_URL}/checkout/success?session_id={{CHECKOUT_SESSION_ID}}",
                'cancel_url': cancel_url or f"{settings.FRONTEND_URL}/checkout/cancel",
                'metadata': checkout_metadata,
                'customer_email': None,  # Lass Stripe die E-Mail abfragen
            })
            
            logger.info(f"Checkout session created for user_id={user_id} price_id={price_id}")
            
            return {
                'checkout_url': session.url,
                'session_id': session.id
            }
            
        except Exception as e:
            logger.error(f"Failed to create checkout session for user_id={user_id}: {e}")
            raise RuntimeError(f"Failed to create checkout: {str(e)}") from e
    
    async def handle_webhook_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verarbeitet Stripe Webhook Events sicher
        
        Args:
            event_data: Stripe Event Payload
            
        Returns:
            Processing result
        """
        event_type = event_data.get('type')
        event_id = event_data.get('id')
        
        logger.info(f"Processing Stripe webhook event_type={event_type} event_id={event_id}")
        
        try:
            if event_type == 'checkout.session.completed':
                return await self._handle_checkout_completed(event_data)
            elif event_type == 'invoice.payment_succeeded':
                return await self._handle_payment_succeeded(event_data)
            elif event_type == 'customer.subscription.updated':
                return await self._handle_subscription_updated(event_data)
            else:
                logger.debug(f"Unhandled webhook event type: {event_type}")
                return {'status': 'ignored', 'reason': f'Event type {event_type} not handled'}
        
        except Exception as e:
            logger.error(f"Failed to process webhook event_id={event_id}: {e}")
            raise RuntimeError(f"Webhook processing failed: {str(e)}") from e
    
    async def _handle_checkout_completed(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verarbeitet erfolgreich abgeschlossene Checkouts"""
        session = event_data.get('data', {}).get('object', {})
        session_id = session.get('id')
        customer_id = session.get('customer')
        metadata = session.get('metadata', {})
        user_id = metadata.get('user_id')
        
        if not user_id:
            logger.warning(f"No user_id in checkout session metadata session_id={session_id}")
            return {'status': 'error', 'reason': 'Missing user_id in metadata'}
        
        # Hier könnte Credits-Vergabe implementiert werden
        logger.info(f"Checkout completed for user_id={user_id} session_id={session_id}")
        
        return {
            'status': 'processed',
            'user_id': user_id,
            'session_id': session_id,
            'customer_id': customer_id
        }
    
    async def _handle_payment_succeeded(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verarbeitet erfolgreiche Zahlungen"""
        # Implementation für wiederkehrende Zahlungen
        return {'status': 'processed'}
    
    async def _handle_subscription_updated(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verarbeitet Subscription-Änderungen"""
        # Implementation für Abo-Verwaltung
        return {'status': 'processed'}
