from __future__ import annotations

import enum
from sqlalchemy import (
    BigInteger, Column, DateTime, ForeignKey, Integer, Text, String, Enum, 
    CheckConstraint, UniqueConstraint, JSON, text, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from .base import Base


class PaymentStatus(enum.Enum):
    """Payment processing states for the state machine."""
    INIT = "INIT"
    PAID = "PAID" 
    CREDITED = "CREDITED"
    REFUNDED = "REFUNDED"
    CHARGEBACK = "CHARGEBACK"
    CANCELED = "CANCELED"
    FAILED = "FAILED"


class StripeCustomer(Base):
    """Legacy Stripe customer mapping - keeping for backward compatibility."""
    __tablename__ = "stripe_customers"

    user_id: Mapped[str] = mapped_column(Text, primary_key=True)
    stripe_customer_id: Mapped[str | None] = mapped_column(Text, unique=True)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=text("now()"), nullable=False)


class Payment(Base):
    """Production-ready payment tracking with full state machine."""
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(Text, nullable=False, index=True)  # Resume Matcher uses Text user IDs
    provider: Mapped[str] = mapped_column(String(50), nullable=False, default="stripe")
    provider_payment_intent_id: Mapped[str | None] = mapped_column(String(255))
    provider_checkout_session_id: Mapped[str | None] = mapped_column(String(255))
    amount_total_cents: Mapped[int] = mapped_column(
        Integer, 
        CheckConstraint("amount_total_cents >= 0"), 
        nullable=False
    )
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="EUR")
    expected_credits: Mapped[int] = mapped_column(
        Integer, 
        CheckConstraint("expected_credits >= 0"), 
        nullable=False
    )
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus), 
        nullable=False, 
        default=PaymentStatus.INIT
    )
    raw_provider_data: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=text("now()"), nullable=False)

    __table_args__ = (
        UniqueConstraint("provider", "provider_payment_intent_id", name="uq_provider_pi"),
        UniqueConstraint("provider", "provider_checkout_session_id", name="uq_provider_cs"),
    )

    # Relationships
    credit_transactions = relationship("CreditTransaction", back_populates="payment")


class CreditTransaction(Base):
    """Immutable audit trail for all credit movements."""
    __tablename__ = "credit_transactions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    payment_id: Mapped[int | None] = mapped_column(
        BigInteger, 
        ForeignKey("payments.id", ondelete="SET NULL")
    )
    admin_action_id: Mapped[int | None] = mapped_column(BigInteger)
    delta_credits: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    meta: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=text("now()"), nullable=False)

    # Relationships
    payment = relationship("Payment", back_populates="credit_transactions")


class ProcessedEvent(Base):
    """Idempotency tracking for webhook events."""
    __tablename__ = "processed_events"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    provider_event_id: Mapped[str] = mapped_column(String(255), nullable=False)
    received_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
    payload_sha256: Mapped[str] = mapped_column(String(64), nullable=False)

    __table_args__ = (
        UniqueConstraint("provider", "provider_event_id", name="uq_provider_event"),
    )


class AdminAction(Base):
    """Audit trail for administrative credit adjustments."""
    __tablename__ = "admin_actions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    actor_user_id: Mapped[str] = mapped_column(Text, nullable=False)
    target_user_id: Mapped[str] = mapped_column(Text, nullable=False)
    delta_credits: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=text("now()"), nullable=False)


# Legacy table - keeping for backward compatibility
class CreditLedger(Base):
    """Legacy credit ledger - keeping for backward compatibility."""
    __tablename__ = "credit_ledger"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[str] = mapped_column(Text, ForeignKey("stripe_customers.user_id", ondelete="RESTRICT"), nullable=False)
    delta: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    stripe_event_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
