"""
Payment provider abstraction layer
Supports multiple payment providers (Stripe primary, extensible for others)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional, Dict, Tuple
from dataclasses import dataclass


@dataclass
class PaymentEvent:
    """Standardized payment event from any provider."""
    provider: str
    event_type: str
    event_id: str
    payload: Dict[str, Any]
    timestamp: Optional[str] = None


class PaymentProvider(ABC):
    """Abstract base class for payment providers."""
    
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def parse_and_verify(self, request_body: bytes, signature_header: str) -> PaymentEvent:
        """Parse and verify webhook payload signature."""
        pass

    @abstractmethod
    async def fetch_line_items_and_credits(self, event: PaymentEvent) -> Tuple[int, int, str]:
        """
        Extract payment details from event.
        Returns: (amount_total_cents, credits, currency)
        """
        pass

    @abstractmethod
    async def get_payment_identity(self, event: PaymentEvent) -> Tuple[Optional[str], Optional[str]]:
        """
        Get payment identifiers.
        Returns: (payment_intent_id, checkout_session_id)
        """
        pass

    @abstractmethod
    async def reconcile_payment(self, provider_payment_intent_id: str) -> Dict[str, Any]:
        """Fetch current payment status from provider for reconciliation."""
        pass

    @abstractmethod
    async def get_user_identifier(self, event: PaymentEvent) -> Optional[str]:
        """Extract user identifier from payment event."""
        pass
