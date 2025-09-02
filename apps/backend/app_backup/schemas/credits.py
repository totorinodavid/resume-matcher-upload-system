"""
Production-ready credit system schemas (Pydantic v2)
Fully typed request/response models with validation
"""

from __future__ import annotations

from typing import Literal, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime


class CreditsResponse(BaseModel):
    """User credits balance response."""
    user_id: str
    credits_balance: int


class AdminAdjustRequest(BaseModel):
    """Administrative credit adjustment request."""
    target_user_id: str = Field(..., min_length=1)
    delta_credits: int = Field(..., description="Can be negative for deductions")
    comment: str = Field(..., min_length=3, max_length=500)


class AdminAdjustResponse(BaseModel):
    """Administrative credit adjustment response."""
    user_id: str
    new_balance: int
    delta_applied: int


class GDPRDeleteRequest(BaseModel):
    """GDPR data deletion request."""
    user_id: str = Field(..., min_length=1)
    anonymize: bool = Field(default=True, description="Anonymize instead of hard delete")


class HealthStatus(BaseModel):
    """Health check response."""
    status: Literal["ok"]


class PaymentStatusResponse(BaseModel):
    """Payment status information."""
    payment_id: int
    user_id: str
    provider: str
    amount_total_cents: int
    currency: str
    expected_credits: int
    status: str
    created_at: datetime
    updated_at: datetime


class CreditTransactionResponse(BaseModel):
    """Credit transaction information."""
    id: int
    user_id: str
    payment_id: Optional[int]
    delta_credits: int
    reason: str
    meta: dict
    created_at: datetime


class PaymentHistoryResponse(BaseModel):
    """User payment history."""
    payments: list[PaymentStatusResponse]
    total_spent_cents: int
    total_credits_purchased: int


class CreditHistoryResponse(BaseModel):
    """User credit transaction history."""
    transactions: list[CreditTransactionResponse]
    current_balance: int
    total_earned: int
    total_spent: int


class WebhookEventResponse(BaseModel):
    """Webhook processing response."""
    ok: bool
    message: Optional[str] = None
    skipped: Optional[str] = None
    credits_added: Optional[int] = None
    user_id: Optional[str] = None


class ReconciliationReport(BaseModel):
    """Daily reconciliation report."""
    processed_payments: int
    credits_reconciled: int
    errors_found: int
    corrections_made: int
    timestamp: datetime


class MetricsResponse(BaseModel):
    """System metrics response."""
    total_payments: int
    total_credits_issued: int
    pending_payments: int
    failed_payments: int
    refunded_payments: int
    timestamp: datetime
