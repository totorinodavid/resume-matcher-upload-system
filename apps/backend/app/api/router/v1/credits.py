from __future__ import annotations

import logging
from uuid import uuid4
from typing import Optional, List

from fastapi import APIRouter, Depends, Request, status, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core import get_db_session
from app.core.auth import require_auth, Principal
from app.core.error_codes import to_error_payload
from app.services.credits_service import CreditsService, InsufficientCreditsError
from app.services.reconciliation import ReconciliationService
from app.schemas.credits import (
    CreditsResponse, 
    PaymentHistoryResponse, 
    CreditHistoryResponse,
    PaymentStatusResponse,
    CreditTransactionResponse,
    ReconciliationReport,
    MetricsResponse
)
from app.models import Payment, CreditTransaction, User

logger = logging.getLogger(__name__)
credits_router = APIRouter()


class DebitRequest(BaseModel):
    delta: int = Field(..., gt=0, description="Number of credits to deduct (positive integer)")
    reason: Optional[str] = Field(default="usage", description="Reason for debit entry")


class UseCreditsRequest(BaseModel):
    units: int = Field(..., gt=0, description="Credits to consume")
    ref: Optional[str] = Field(default=None, max_length=128, description="Reference for the debit entry (short)")


# ===== USER ENDPOINTS =====

@credits_router.get("/me/hello", summary="Echo the authenticated NextAuth user id")
async def me_hello(principal: Principal = Depends(require_auth)):
    return {"data": {"user": principal.user_id}}


@credits_router.get("/me/credits", summary="Get current user's credit balance", response_model=dict)
async def get_my_credits(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    principal: Principal = Depends(require_auth),
):
    """
    Get the authenticated user's current credit balance.
    Production-ready with proper error handling and response format.
    """
    request_id = getattr(request.state, "request_id", str(uuid4()))
    try:
        svc = CreditsService(db)
        balance = await svc.get_balance(user_id=principal.user_id)
        
        # Return in both legacy format and new format for compatibility
        return JSONResponse(content={
            "request_id": request_id, 
            "data": {
                "balance": int(balance),
                "user_id": principal.user_id,
                "credits_balance": int(balance)
            }
        })
    except Exception as e:
        code, payload = to_error_payload(e, request_id)
        return JSONResponse(status_code=code, content=payload)


@credits_router.get("/me/payments", summary="Get user's payment history")
async def get_my_payment_history(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    principal: Principal = Depends(require_auth),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0)
):
    """Get authenticated user's payment history with pagination."""
    request_id = getattr(request.state, "request_id", str(uuid4()))
    try:
        # Fetch user's payments
        stmt = (
            select(Payment)
            .where(Payment.user_id == principal.user_id)
            .order_by(desc(Payment.created_at))
            .limit(limit)
            .offset(offset)
        )
        result = await db.execute(stmt)
        payments = result.scalars().all()
        
        # Calculate totals
        total_spent = sum(p.amount_total_cents for p in payments)
        total_credits = sum(p.expected_credits for p in payments)
        
        payment_responses = [
            PaymentStatusResponse(
                payment_id=p.id,
                user_id=p.user_id,
                provider=p.provider,
                amount_total_cents=p.amount_total_cents,
                currency=p.currency,
                expected_credits=p.expected_credits,
                status=p.status.value,
                created_at=p.created_at,
                updated_at=p.updated_at
            ) for p in payments
        ]
        
        response = PaymentHistoryResponse(
            payments=payment_responses,
            total_spent_cents=total_spent,
            total_credits_purchased=total_credits
        )
        
        return JSONResponse(content={
            "request_id": request_id,
            "data": response.model_dump()
        })
        
    except Exception as e:
        code, payload = to_error_payload(e, request_id)
        return JSONResponse(status_code=code, content=payload)


@credits_router.get("/me/credit-history", summary="Get user's credit transaction history")
async def get_my_credit_history(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    principal: Principal = Depends(require_auth),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0)
):
    """Get authenticated user's credit transaction history."""
    request_id = getattr(request.state, "request_id", str(uuid4()))
    try:
        # Fetch credit transactions
        stmt = (
            select(CreditTransaction)
            .where(CreditTransaction.user_id == principal.user_id)
            .order_by(desc(CreditTransaction.created_at))
            .limit(limit)
            .offset(offset)
        )
        result = await db.execute(stmt)
        transactions = result.scalars().all()
        
        # Get current balance
        svc = CreditsService(db)
        current_balance = await svc.get_balance(user_id=principal.user_id)
        
        # Calculate totals
        total_earned = sum(t.delta_credits for t in transactions if t.delta_credits > 0)
        total_spent = abs(sum(t.delta_credits for t in transactions if t.delta_credits < 0))
        
        transaction_responses = [
            CreditTransactionResponse(
                id=t.id,
                user_id=t.user_id,
                payment_id=t.payment_id,
                delta_credits=t.delta_credits,
                reason=t.reason,
                meta=t.meta,
                created_at=t.created_at
            ) for t in transactions
        ]
        
        response = CreditHistoryResponse(
            transactions=transaction_responses,
            current_balance=current_balance,
            total_earned=total_earned,
            total_spent=total_spent
        )
        
        return JSONResponse(content={
            "request_id": request_id,
            "data": response.model_dump()
        })
        
    except Exception as e:
        code, payload = to_error_payload(e, request_id)
        return JSONResponse(status_code=code, content=payload)


# ===== LEGACY ENDPOINTS =====

@credits_router.post("/credits/debit", summary="Debit credits for usage")
async def debit_credits(
    request: Request,
    body: DebitRequest,
    db: AsyncSession = Depends(get_db_session),
    principal: Principal = Depends(require_auth),
):
    request_id = getattr(request.state, "request_id", str(uuid4()))
    try:
        svc = CreditsService(db)
        await svc.debit_usage(
            user_id=principal.user_id,
            delta=body.delta,
            reason=body.reason or "usage",
        )
        new_balance = await svc.get_balance(user_id=principal.user_id)
        return JSONResponse(content={"request_id": request_id, "data": {"balance": int(new_balance)}})
    except InsufficientCreditsError as e:
        # Phase 6 spec: strict shape { error: "Not enough credits" }
        return JSONResponse(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            content={"request_id": request_id, "error": "Not enough credits"},
        )
    except Exception as e:
        code, payload = to_error_payload(e, request_id)
        return JSONResponse(status_code=code, content=payload)


@credits_router.post("/use-credits", summary="Consume credits (alias to debit)")
async def use_credits(
    request: Request,
    body: UseCreditsRequest,
    db: AsyncSession = Depends(get_db_session),
    principal: Principal = Depends(require_auth),
):
    request_id = getattr(request.state, "request_id", str(uuid4()))
    try:
        svc = CreditsService(db)
        logger.info(
            "use_credits request",
            extra={"user": principal.user_id, "units": body.units, "ref": (body.ref or "usage")[:64]},
        )
        await svc.debit_usage(
            user_id=principal.user_id,
            delta=body.units,
            reason=body.ref or "usage",
        )
        # Phase 6 spec: return success boolean
        return JSONResponse(content={"request_id": request_id, "data": {"ok": True}})
    except InsufficientCreditsError:
        return JSONResponse(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            content={"request_id": request_id, "error": "Not enough credits"},
        )
    except Exception as e:
        code, payload = to_error_payload(e, request_id)
        return JSONResponse(status_code=code, content=payload)


# ===== ADMIN ENDPOINTS =====

@credits_router.get("/admin/metrics", summary="Get system metrics (admin only)")
async def get_admin_metrics(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    # TODO: Add admin auth check
):
    """Get system-wide payment and credit metrics."""
    request_id = getattr(request.state, "request_id", str(uuid4()))
    try:
        reconciliation_service = ReconciliationService()
        metrics = await reconciliation_service.get_reconciliation_metrics(db)
        
        return JSONResponse(content={
            "request_id": request_id,
            "data": metrics
        })
        
    except Exception as e:
        code, payload = to_error_payload(e, request_id)
        return JSONResponse(status_code=code, content=payload)


@credits_router.post("/admin/reconcile", summary="Trigger manual reconciliation (admin only)")
async def trigger_reconciliation(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    limit: int = Query(default=200, ge=1, le=1000),
    # TODO: Add admin auth check
):
    """Manually trigger payment reconciliation with Stripe."""
    request_id = getattr(request.state, "request_id", str(uuid4()))
    try:
        reconciliation_service = ReconciliationService()
        stats = await reconciliation_service.reconcile_payments(db, limit)
        
        return JSONResponse(content={
            "request_id": request_id,
            "data": {
                "reconciliation_stats": stats,
                "message": "Reconciliation completed successfully"
            }
        })
        
    except Exception as e:
        code, payload = to_error_payload(e, request_id)
        return JSONResponse(status_code=code, content=payload)


# ===== LEGACY WEBHOOK STUB =====

@credits_router.post("/stripe/webhook", summary="Stripe webhook (legacy stub)")
async def stripe_webhook_legacy(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Legacy webhook stub for backward compatibility.
    
    The production webhook handler is at /webhooks/stripe
    """
    request_id = getattr(request.state, "request_id", str(uuid4()))
    try:
        raw = await request.body()
        sig = request.headers.get("Stripe-Signature", "")
        logger.warning(
            "Legacy webhook endpoint called - use /webhooks/stripe instead",
            extra={"bytes": len(raw), "sig_present": bool(sig)}
        )
        return JSONResponse(status_code=status.HTTP_200_OK, content={"ok": True, "message": "Use /webhooks/stripe"})
    except Exception as e:
        code, payload = to_error_payload(e, request_id)
        return JSONResponse(status_code=code, content=payload)
