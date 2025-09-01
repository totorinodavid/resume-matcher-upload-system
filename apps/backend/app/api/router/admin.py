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
        from_balance = await credits_service.get_user_credits(request.from_user_id)
        if not from_balance or from_balance.total_credits < request.amount:
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient credits. Available: {from_balance.total_credits if from_balance else 0}"
            )
        
        # Execute transfer
        await credits_service.subtract_credits(request.from_user_id, request.amount)
        await credits_service.add_credits(request.to_user_id, request.amount)
        
        await db.commit()
        
        # Get final balances
        from_final = await credits_service.get_user_credits(request.from_user_id)
        to_final = await credits_service.get_user_credits(request.to_user_id)
        
        logger.info(f"Transfer completed: {request.amount} credits moved")
        
        return {
            "success": True,
            "transferred": request.amount,
            "from_user_final_balance": from_final.total_credits if from_final else 0,
            "to_user_final_balance": to_final.total_credits if to_final else 0
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
        balance = await credits_service.get_user_credits(user_id)
        
        return CreditBalanceResponse(
            user_id=user_id,
            total_credits=balance.total_credits if balance else 0,
            found=balance is not None
        )
        
    except Exception as e:
        logger.error(f"Failed to get credits for {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
