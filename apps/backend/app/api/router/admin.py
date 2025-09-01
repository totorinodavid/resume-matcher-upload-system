#!/usr/bin/env python3
"""
Emergency Credits Admin Endpoint
Add admin endpoint to transfer credits between users
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db_session
from app.services.credits_service import CreditsService
from pydantic import BaseModel
from typing import Optional
import logging

logger = logging.getLogger(__name__)

admin_router = APIRouter(prefix="/admin", tags=["admin"])

class CreditTransferRequest(BaseModel):
    from_user_id: str
    to_user_id: str
    amount: int
    reason: str = "admin_transfer"

class CreditBalanceResponse(BaseModel):
    user_id: str
    total_credits: int
    found: bool

@admin_router.post("/add-credits")
async def add_credits_directly(
    request: CreditTransferRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """Add credits directly to a user - EMERGENCY ADMIN FUNCTION"""
    
    logger.info(f"Direct credit addition: {request.amount} credits to {request.to_user_id}")
    
    try:
        from app.models import CreditLedger
        
        credits_service = CreditsService(db)
        
        # Ensure customer exists
        await credits_service.ensure_customer(user_id=request.to_user_id)
        
        # Add credits directly using credit_purchase
        await credits_service.credit_purchase(
            user_id=request.to_user_id,
            delta=request.amount,
            reason=f"admin_direct_add:{request.reason}",
            stripe_event_id=None,
        )
        
        await db.commit()
        
        # Get final balance
        final_balance = await credits_service.get_balance(user_id=request.to_user_id)
        
        logger.info(f"Direct credit addition completed: {request.amount} credits added")
        
        return {
            "success": True,
            "method": "direct_add",
            "credits_added": request.amount,
            "user_id": request.to_user_id,
            "final_balance": final_balance,
            "reason": request.reason
        }
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Direct credit addition failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.post("/force-transfer-credits")
async def force_transfer_credits(
    request: CreditTransferRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """Force transfer credits between users - bypasses balance checks for admin fixes"""
    
    logger.info(f"FORCE transfer: {request.amount} credits from {request.from_user_id} to {request.to_user_id}")
    
    try:
        from app.models import CreditLedger
        
        # Get current balances for logging
        credits_service = CreditsService(db)
        from_balance = await credits_service.get_balance(user_id=request.from_user_id)
        to_balance = await credits_service.get_balance(user_id=request.to_user_id)
        
        logger.info(f"Before transfer - From: {from_balance}, To: {to_balance}")
        
        # Direct database operations - bypass service layer restrictions
        # Remove credits from source user (negative entry)
        debit_entry = CreditLedger(
            user_id=request.from_user_id,
            delta=-request.amount,
            reason=f"force_transfer_to_{request.to_user_id}",
            stripe_event_id=None,
        )
        db.add(debit_entry)
        
        # Add credits to target user (positive entry)
        credit_entry = CreditLedger(
            user_id=request.to_user_id,
            delta=request.amount,
            reason=f"force_transfer_from_{request.from_user_id}",
            stripe_event_id=None,
        )
        db.add(credit_entry)
        
        await db.flush()
        await db.commit()
        
        # Get final balances
        from_final = await credits_service.get_balance(user_id=request.from_user_id)
        to_final = await credits_service.get_balance(user_id=request.to_user_id)
        
        logger.info(f"After transfer - From: {from_final}, To: {to_final}")
        
        return {
            "success": True,
            "method": "force_transfer",
            "transferred": request.amount,
            "from_user_initial": from_balance,
            "from_user_final_balance": from_final,
            "to_user_initial": to_balance,
            "to_user_final_balance": to_final
        }
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Force transfer failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.post("/transfer-credits")
async def transfer_credits(
    request: CreditTransferRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """Transfer credits between users - ADMIN ONLY"""
    
    # Simple admin check (in production, add proper auth)
    logger.info(f"Credit transfer request: {request.amount} credits from {request.from_user_id} to {request.to_user_id}")
    
    try:
        credits_service = CreditsService(db)
        
        # Check source balance
        from_balance = await credits_service.get_balance(user_id=request.from_user_id)
        if from_balance < request.amount:
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient credits. Available: {from_balance}"
            )
        
        # Execute transfer
        await credits_service.debit_usage(user_id=request.from_user_id, delta=request.amount, reason=f"transfer_to_{request.to_user_id}")
        await credits_service.credit_purchase(user_id=request.to_user_id, delta=request.amount, reason=f"transfer_from_{request.from_user_id}", stripe_event_id=None)
        
        await db.commit()
        
        # Get final balances
        from_final = await credits_service.get_balance(user_id=request.from_user_id)
        to_final = await credits_service.get_balance(user_id=request.to_user_id)
        
        logger.info(f"Transfer completed: {request.amount} credits moved")
        
        return {
            "success": True,
            "transferred": request.amount,
            "from_user_final_balance": from_final,
            "to_user_final_balance": to_final
        }
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Transfer failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.get("/credits/{user_id}", response_model=CreditBalanceResponse)
async def get_user_credits(
    user_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Get credit balance for a user"""
    
    try:
        credits_service = CreditsService(db)
        balance = await credits_service.get_balance(user_id=user_id)
        
        return CreditBalanceResponse(
            user_id=user_id,
            total_credits=balance,
            found=True
        )
        
    except Exception as e:
        logger.error(f"Failed to get credits for {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
