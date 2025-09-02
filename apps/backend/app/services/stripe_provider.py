"""
Stripe payment provider implementation
Production-ready with full error handling and security
"""

from __future__ import annotations

import hashlib
import logging
from typing import Any, Dict, Optional, Tuple, List

try:
    import stripe
except ImportError:
    stripe = None

from app.core import settings
from app.services.payment_provider import PaymentProvider, PaymentEvent

logger = logging.getLogger(__name__)


class StripeEvent(PaymentEvent):
    """Stripe-specific payment event wrapper."""
    
    def __init__(self, stripe_event: Dict[str, Any]):
        super().__init__(
            provider="stripe",
            event_type=stripe_event["type"],
            event_id=stripe_event["id"],
            payload=stripe_event,
            timestamp=stripe_event.get("created")
        )


class StripeProvider(PaymentProvider):
    """Production-ready Stripe payment provider."""
    
    def __init__(self):
        super().__init__("stripe")
        if stripe and settings.STRIPE_SECRET_KEY:
            stripe.api_key = settings.STRIPE_SECRET_KEY

    async def parse_and_verify(self, request_body: bytes, signature_header: str) -> StripeEvent:
        """Parse and verify Stripe webhook with signature validation."""
        if not stripe:
            raise ImportError("Stripe module not available")
        
        if not settings.STRIPE_WEBHOOK_SECRET:
            raise ValueError("Stripe webhook secret not configured")
        
        try:
            event = stripe.Webhook.construct_event(
                payload=request_body.decode("utf-8"),
                sig_header=signature_header,
                secret=settings.STRIPE_WEBHOOK_SECRET,
                tolerance=getattr(settings, 'STRIPE_TOLERANCE_SECONDS', 300)
            )
            return StripeEvent(event)
        except stripe.error.SignatureVerificationError as e:
            logger.warning(f"Invalid Stripe webhook signature: {e}")
            raise ValueError("Invalid webhook signature") from e
        except Exception as e:
            logger.error(f"Error parsing Stripe webhook: {e}")
            raise ValueError("Invalid webhook payload") from e

    async def get_user_identifier(self, event: StripeEvent) -> Optional[str]:
        """Extract user ID from Stripe event metadata or customer reference."""
        obj = event.payload["data"]["object"]
        
        # Try client_reference_id from checkout session first
        if obj.get("object") == "checkout.session":
            user_id = obj.get("client_reference_id")
            if user_id:
                return str(user_id)
        
        # Try metadata.user_id from any object
        metadata = obj.get("metadata", {})
        if isinstance(metadata, dict) and "user_id" in metadata:
            return str(metadata["user_id"])
        
        # For payment_intent events, get from metadata
        pi_id = None
        if obj.get("object") == "payment_intent":
            pi_id = obj["id"]
        elif obj.get("object") == "charge":
            pi_id = obj.get("payment_intent")
        elif obj.get("object") == "refund":
            charge_id = obj.get("charge")
            if charge_id and stripe:
                try:
                    charge = stripe.Charge.retrieve(charge_id)
                    pi_id = charge.get("payment_intent")
                except Exception as e:
                    logger.warning(f"Failed to retrieve charge {charge_id}: {e}")
        
        if pi_id and stripe:
            try:
                pi = stripe.PaymentIntent.retrieve(pi_id)
                metadata = pi.get("metadata", {})
                if isinstance(metadata, dict) and "user_id" in metadata:
                    return str(metadata["user_id"])
            except Exception as e:
                logger.warning(f"Failed to retrieve payment intent {pi_id}: {e}")
        
        return None

    async def get_payment_identity(self, event: StripeEvent) -> Tuple[Optional[str], Optional[str]]:
        """Get payment intent ID and checkout session ID."""
        obj = event.payload["data"]["object"]
        payment_intent_id = None
        checkout_session_id = None
        
        if obj.get("object") == "checkout.session":
            checkout_session_id = obj["id"]
            payment_intent_id = obj.get("payment_intent")
        elif obj.get("object") == "payment_intent":
            payment_intent_id = obj["id"]
        elif obj.get("object") == "charge":
            payment_intent_id = obj.get("payment_intent")
        elif obj.get("object") == "refund":
            charge_id = obj.get("charge")
            if charge_id and stripe:
                try:
                    charge = stripe.Charge.retrieve(charge_id)
                    payment_intent_id = charge.get("payment_intent")
                except Exception as e:
                    logger.warning(f"Failed to retrieve charge {charge_id}: {e}")
        
        return payment_intent_id, checkout_session_id

    async def fetch_line_items_and_credits(self, event: StripeEvent) -> Tuple[int, int, str]:
        """Extract amount, credits, and currency from Stripe event."""
        obj = event.payload["data"]["object"]
        amount_total = 0
        credits = 0
        currency = "EUR"
        
        # Get basic payment details
        if obj.get("object") == "checkout.session":
            amount_total = obj.get("amount_total", 0)
            currency = (obj.get("currency") or "eur").upper()
            
            # Try to get credits from session metadata first
            metadata = obj.get("metadata", {})
            if isinstance(metadata, dict) and "credits" in metadata:
                try:
                    credits = int(metadata["credits"])
                except (ValueError, TypeError):
                    credits = 0
            
            # If no credits in metadata, fetch from line items
            if credits == 0 and stripe:
                try:
                    session_id = obj["id"]
                    line_items = stripe.checkout.Session.list_line_items(session_id, limit=10)
                    total_credits = 0
                    
                    for item in line_items.get("data", []):
                        price = item.get("price", {})
                        price_metadata = price.get("metadata", {})
                        item_credits = 0
                        
                        if isinstance(price_metadata, dict) and "credits" in price_metadata:
                            try:
                                item_credits = int(price_metadata["credits"])
                            except (ValueError, TypeError):
                                item_credits = 0
                        
                        quantity = item.get("quantity", 1)
                        total_credits += item_credits * quantity
                    
                    credits = total_credits
                except Exception as e:
                    logger.warning(f"Failed to fetch line items for session {obj.get('id')}: {e}")
        
        elif obj.get("object") == "payment_intent":
            amount_total = obj.get("amount", 0)
            currency = (obj.get("currency") or "eur").upper()
            
            metadata = obj.get("metadata", {})
            if isinstance(metadata, dict) and "credits" in metadata:
                try:
                    credits = int(metadata["credits"])
                except (ValueError, TypeError):
                    credits = 0
        
        else:
            # For other object types, try to get from payment intent
            pi_id = obj.get("payment_intent")
            if pi_id and stripe:
                try:
                    pi = stripe.PaymentIntent.retrieve(pi_id)
                    amount_total = pi.get("amount", 0)
                    currency = (pi.get("currency") or "eur").upper()
                    
                    metadata = pi.get("metadata", {})
                    if isinstance(metadata, dict) and "credits" in metadata:
                        try:
                            credits = int(metadata["credits"])
                        except (ValueError, TypeError):
                            credits = 0
                except Exception as e:
                    logger.warning(f"Failed to retrieve payment intent {pi_id}: {e}")
        
        return int(amount_total or 0), int(credits or 0), currency

    async def reconcile_payment(self, provider_payment_intent_id: str) -> Dict[str, Any]:
        """Fetch current payment status from Stripe for reconciliation."""
        if not stripe:
            raise ImportError("Stripe module not available")
        
        try:
            payment_intent = stripe.PaymentIntent.retrieve(provider_payment_intent_id)
            return dict(payment_intent)
        except Exception as e:
            logger.error(f"Failed to reconcile payment {provider_payment_intent_id}: {e}")
            raise ValueError(f"Failed to fetch payment intent: {e}") from e

    def _get_price_to_credits_mapping(self) -> Dict[str, int]:
        """Get price ID to credits mapping from configuration."""
        mapping = {}
        
        # Try JSON mapping first
        if hasattr(settings, 'STRIPE_PRICE_TO_CREDITS_JSON') and settings.STRIPE_PRICE_TO_CREDITS_JSON:
            try:
                import json
                data = json.loads(settings.STRIPE_PRICE_TO_CREDITS_JSON)
                if isinstance(data, dict):
                    for price_id, credits in data.items():
                        try:
                            mapping[str(price_id)] = int(credits)
                        except (ValueError, TypeError):
                            continue
            except (json.JSONDecodeError, Exception) as e:
                logger.warning(f"Invalid STRIPE_PRICE_TO_CREDITS_JSON: {e}")
        
        # Fallback to individual price settings
        price_configs = [
            (getattr(settings, "STRIPE_PRICE_SMALL_ID", None), 
             getattr(settings, "STRIPE_PRICE_SMALL_CREDITS", 100)),
            (getattr(settings, "STRIPE_PRICE_MEDIUM_ID", None), 
             getattr(settings, "STRIPE_PRICE_MEDIUM_CREDITS", 500)),
            (getattr(settings, "STRIPE_PRICE_LARGE_ID", None), 
             getattr(settings, "STRIPE_PRICE_LARGE_CREDITS", 1500)),
        ]
        
        for price_id, credits in price_configs:
            if price_id:
                try:
                    mapping[str(price_id)] = int(credits)
                except (ValueError, TypeError):
                    continue
        
        return mapping
