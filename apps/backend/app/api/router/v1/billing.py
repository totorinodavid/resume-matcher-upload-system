"""
Billing API Router - Sichere Stripe-Operationen
Alle Stripe Secret-Keys bleiben im Backend
"""
import logging
from typing import Optional
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.core.database import get_db_session
from app.core.auth import require_auth, Principal
from app.services.billing_service import BillingService
from app.core.error_codes import to_error_payload

logger = logging.getLogger(__name__)
billing_router = APIRouter(tags=["billing"])


class CreatePortalSessionRequest(BaseModel):
    return_url: Optional[str] = Field(
        default=None,
        description="URL to redirect to after portal session ends"
    )


class CreateCheckoutSessionRequest(BaseModel):
    price_id: str = Field(..., description="Stripe Price ID for the product")
    success_url: Optional[str] = Field(default=None, description="Success redirect URL")
    cancel_url: Optional[str] = Field(default=None, description="Cancel redirect URL")
    metadata: Optional[dict] = Field(default=None, description="Additional metadata")


@billing_router.post(
    "/portal/create",
    summary="Create Stripe Billing Portal Session",
    description="Creates a secure billing portal session. All Stripe secrets handled server-side."
)
async def create_billing_portal(
    request: Request,
    payload: CreatePortalSessionRequest,
    db: AsyncSession = Depends(get_db_session),
    principal: Principal = Depends(require_auth),
):
    """
    Erstellt eine sichere Stripe Billing Portal Session.
    
    Security:
    - Stripe Secret Key bleibt im Backend
    - User muss authentifiziert sein
    - Rate limiting angewendet
    """
    request_id = getattr(request.state, "request_id", str(uuid4()))
    user_id = principal.user_id
    
    if not user_id:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "request_id": request_id,
                "error": {
                    "code": "UNAUTHORIZED",
                    "message": "User authentication required"
                }
            }
        )
    
    try:
        billing_service = BillingService(db)
        
        result = await billing_service.create_billing_portal_session(
            user_id=user_id,
            return_url=payload.return_url
        )
        
        logger.info(f"Billing portal created for user_id={user_id} request_id={request_id}")
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "request_id": request_id,
                "data": {
                    "url": result["portal_url"],
                    "session_id": result["session_id"]
                }
            }
        )
        
    except ValueError as e:
        logger.warning(f"Validation error in billing portal creation: {e}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "request_id": request_id,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": str(e)
                }
            }
        )
        
    except RuntimeError as e:
        logger.error(f"Runtime error in billing portal creation: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "request_id": request_id,
                "error": {
                    "code": "STRIPE_ERROR",
                    "message": "Failed to create billing portal"
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Unexpected error in billing portal creation: {e}")
        code, body = to_error_payload(e, request_id)
        return JSONResponse(status_code=code, content=body)


@billing_router.post(
    "/checkout/create",
    summary="Create Stripe Checkout Session",
    description="Creates a secure checkout session for purchasing credits or subscriptions."
)
async def create_checkout_session(
    request: Request,
    payload: CreateCheckoutSessionRequest,
    db: AsyncSession = Depends(get_db_session),
    principal: Principal = Depends(require_auth),
):
    """
    Erstellt eine sichere Stripe Checkout Session.
    """
    request_id = getattr(request.state, "request_id", str(uuid4()))
    user_id = principal.user_id
    
    if not user_id:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "request_id": request_id,
                "error": {
                    "code": "UNAUTHORIZED", 
                    "message": "User authentication required"
                }
            }
        )
    
    try:
        billing_service = BillingService(db)
        
        result = await billing_service.create_checkout_session(
            user_id=user_id,
            price_id=payload.price_id,
            success_url=payload.success_url,
            cancel_url=payload.cancel_url,
            metadata=payload.metadata
        )
        
        logger.info(f"Checkout session created for user_id={user_id} price_id={payload.price_id}")
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "request_id": request_id,
                "data": {
                    "url": result["checkout_url"],
                    "session_id": result["session_id"]
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to create checkout session: {e}")
        code, body = to_error_payload(e, request_id)
        return JSONResponse(status_code=code, content=body)


@billing_router.get(
    "/status",
    summary="Get user billing status",
    description="Returns current billing/subscription status for authenticated user."
)
async def get_billing_status(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    principal: Principal = Depends(require_auth),
):
    """
    Holt den aktuellen Billing-Status für den User.
    """
    request_id = getattr(request.state, "request_id", str(uuid4()))
    user_id = principal.user_id
    
    try:
        # Hier könnte Status aus StripeCustomer und CreditLedger geholt werden
        # Vorerst Dummy-Response
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "request_id": request_id,
                "data": {
                    "user_id": user_id,
                    "has_stripe_customer": False,  # TODO: Implementieren
                    "subscription_status": None,   # TODO: Implementieren
                    "credit_balance": 0           # TODO: Implementieren
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to get billing status: {e}")
        code, body = to_error_payload(e, request_id)
        return JSONResponse(status_code=code, content=body)
