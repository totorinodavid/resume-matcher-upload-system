"""
🚨 EMERGENCY ADMIN ENDPOINT - Credit Transfer
Fast API endpoint to transfer credits between users for emergency user ID mismatch fix
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
import logging

from app.core.database import get_db_session
from app.services.credits_service import CreditsService

# Emergency admin router
emergency_router = APIRouter(prefix="/api/v1/emergency", tags=["emergency"])

logger = logging.getLogger(__name__)

class CreditTransferRequest(BaseModel):
    from_user_id: str
    to_user_id: str
    credits: int
    reason: str
    emergency_code: Optional[str] = None

class CreditTransferResponse(BaseModel):
    success: bool
    message: str
    from_user_balance: int
    to_user_balance: int

@emergency_router.post("/transfer-credits", response_model=CreditTransferResponse)
async def emergency_credit_transfer(
    request: CreditTransferRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """
    🚨 EMERGENCY CREDIT TRANSFER
    Transfers credits between users for user ID mismatch fixes
    
    SECURITY: Should be protected in production
    USE CASE: When Stripe payment goes to wrong user due to user ID mapping issues
    """
    
    # Emergency validation (in production, add proper admin auth)
    if request.emergency_code != "user_id_mismatch_fix_2025":
        raise HTTPException(status_code=403, detail="Invalid emergency code")
    
    if request.credits <= 0:
        raise HTTPException(status_code=400, detail="Credits must be positive")
    
    if request.from_user_id == request.to_user_id:
        raise HTTPException(status_code=400, detail="Cannot transfer to same user")
    
    logger.info(f"🚨 EMERGENCY CREDIT TRANSFER: {request.credits} credits from {request.from_user_id} to {request.to_user_id}")
    logger.info(f"   Reason: {request.reason}")
    
    try:
        credits_service = CreditsService(db)
        
        # Get current balances
        from_balance_before = await credits_service.get_balance(user_id=request.from_user_id)
        to_balance_before = await credits_service.get_balance(user_id=request.to_user_id)
        
        logger.info(f"   From user balance before: {from_balance_before}")
        logger.info(f"   To user balance before: {to_balance_before}")
        
        # Check if from_user has enough credits
        if from_balance_before < request.credits:
            raise HTTPException(
                status_code=400, 
                detail=f"From user has insufficient credits: {from_balance_before} < {request.credits}"
            )
        
        # Perform transfer:
        # 1. Debit from source user
        await credits_service.debit_usage(
            user_id=request.from_user_id,
            delta=request.credits,
            reason=f"Emergency transfer TO {request.to_user_id}: {request.reason}"
        )
        
        # 2. Credit to destination user  
        await credits_service.credit_purchase(
            user_id=request.to_user_id,
            delta=request.credits,
            reason=f"Emergency transfer FROM {request.from_user_id}: {request.reason}",
            stripe_event_id=None  # Not a Stripe event
        )
        
        # Commit the transaction
        await db.commit()
        
        # Get final balances
        from_balance_after = await credits_service.get_balance(user_id=request.from_user_id)
        to_balance_after = await credits_service.get_balance(user_id=request.to_user_id)
        
        logger.info(f"✅ TRANSFER COMPLETE:")
        logger.info(f"   From user balance after: {from_balance_after}")
        logger.info(f"   To user balance after: {to_balance_after}")
        
        return CreditTransferResponse(
            success=True,
            message=f"Successfully transferred {request.credits} credits",
            from_user_balance=from_balance_after,
            to_user_balance=to_balance_after
        )
        
    except Exception as e:
        await db.rollback()
        logger.error(f"❌ EMERGENCY TRANSFER FAILED: {e}")
        raise HTTPException(status_code=500, detail=f"Transfer failed: {str(e)}")

@emergency_router.get("/user/{user_id}/credits")
async def get_user_credits_emergency(
    user_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """
    🔍 Emergency endpoint to check user credits
    """
    try:
        credits_service = CreditsService(db)
        balance = await credits_service.get_balance(user_id=user_id)
        
        return {
            "user_id": user_id,
            "credits": balance,
            "status": "active"
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting credits for {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get credits: {str(e)}")

# Add simple credit addition endpoint for manual fixes
@emergency_router.post("/user/{user_id}/add-credits")
async def emergency_add_credits(
    user_id: str,
    credits: int,
    reason: str,
    emergency_code: str,
    db: AsyncSession = Depends(get_db_session)
):
    """
    🚨 EMERGENCY ADD CREDITS
    Adds credits to a user for emergency fixes
    """
    
    if emergency_code != "user_id_mismatch_fix_2025":
        raise HTTPException(status_code=403, detail="Invalid emergency code")
    
    if credits <= 0:
        raise HTTPException(status_code=400, detail="Credits must be positive")
    
    logger.info(f"🚨 EMERGENCY ADD CREDITS: {credits} to {user_id}")
    logger.info(f"   Reason: {reason}")
    
    try:
        credits_service = CreditsService(db)
        
        # Get balance before
        balance_before = await credits_service.get_balance(user_id=user_id)
        
        # Add credits
        await credits_service.credit_purchase(
            user_id=user_id,
            delta=credits,
            reason=f"Emergency manual addition: {reason}",
            stripe_event_id=None
        )
        
        await db.commit()
        
        # Get balance after
        balance_after = await credits_service.get_balance(user_id=user_id)
        
        logger.info(f"✅ CREDITS ADDED:")
        logger.info(f"   Before: {balance_before}")
        logger.info(f"   After: {balance_after}")
        
        return {
            "success": True,
            "message": f"Added {credits} credits to user {user_id}",
            "balance_before": balance_before,
            "balance_after": balance_after
        }
        
    except Exception as e:
        await db.rollback()
        logger.error(f"❌ EMERGENCY ADD CREDITS FAILED: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add credits: {str(e)}")
