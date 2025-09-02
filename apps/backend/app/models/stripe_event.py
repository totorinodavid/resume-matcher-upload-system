"""
Stripe Event model for webhook event deduplication.
Used to ensure idempotent webhook processing.
"""

from sqlalchemy import Column, String, DateTime, Text, JSON
from sqlalchemy.sql import func
from ..models.base import Base


class StripeEvent(Base):
    """
    Model for tracking processed Stripe webhook events.
    Ensures idempotent webhook processing by preventing duplicate event handling.
    """
    __tablename__ = "stripe_events"

    # Stripe event ID - primary key for deduplication
    event_id = Column(String(255), primary_key=True, index=True)
    
    # Event metadata
    event_type = Column(String(100), nullable=False, index=True)
    processed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Store raw event data for debugging/audit
    raw_data = Column(JSON, nullable=True)
    
    # Processing status and error tracking
    processing_status = Column(String(50), default="completed", nullable=False)
    error_message = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<StripeEvent(id='{self.event_id}', type='{self.event_type}', status='{self.processing_status}')>"
