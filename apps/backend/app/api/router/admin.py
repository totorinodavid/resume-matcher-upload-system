#!/usr/bin/env python3
"""
🚨 EMERGENCY CREDITS ADMIN ENDPOINTS 🚨
Fixed credit assignment for Stripe payments
Add emergency admin endpoints for credit management and database diagnosis
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.core.database import get_db_session
from app.services.credits_service import CreditsService
from app.models.user import User
from app.models import CreditLedger
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
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

class EmergencyUserCreation(BaseModel):
    email: str
    name: str
    user_uuid: Optional[str] = None

class EmergencyCreditAssignment(BaseModel):
    user_id: str
    credits: int
    reason: str
    stripe_event: Optional[str] = None
    admin_note: Optional[str] = None

# 🚨 EMERGENCY ENDPOINTS FOR IMMEDIATE CREDIT FIX 🚨

@admin_router.get("/debug/database-schema")
async def get_database_schema(db: AsyncSession = Depends(get_db_session)):
    """Emergency: Get actual database schema"""
    try:
        # Get User table columns
        result = await db.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'users'"))
        columns = [row[0] for row in result.fetchall()]
        
        return {
            "user_table_columns": columns,
            "minimal_columns": ["id", "email", "name"],
            "schema_discovery": "emergency_mode"
        }
    except Exception as e:
        logger.error(f"Schema discovery failed: {e}")
        return {"error": str(e), "fallback": "minimal_schema"}

@admin_router.get("/debug/all-users")
async def get_all_users(db: AsyncSession = Depends(get_db_session)):
    """Emergency: List all users in database"""
    try:
        result = await db.execute(select(User))
        users = result.scalars().all()
        
        return {
            "users": [
                {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name
                }
                for user in users
            ],
            "total_count": len(users)
        }
    except Exception as e:
        logger.error(f"User listing failed: {e}")
        return {"error": str(e), "users": []}

@admin_router.get("/debug/credits/{user_id}")
async def get_user_credits_debug(user_id: str, db: AsyncSession = Depends(get_db_session)):
    """Emergency: Get credit balance for any user ID"""
    try:
        credits_service = CreditsService(db)
        balance = await credits_service.get_balance(user_id=user_id)
        
        return {
            "user_id": user_id,
            "credits": balance,
            "debug_mode": True
        }
    except Exception as e:
        logger.error(f"Credit check failed for {user_id}: {e}")
        return {"error": str(e), "credits": 0}

@admin_router.get("/debug/search-users")
async def search_users_debug(q: str, db: AsyncSession = Depends(get_db_session)):
    """Emergency: Search users by any term"""
    try:
        # Search by ID, email, or name
        result = await db.execute(
            select(User).where(
                User.id.like(f"%{q}%") |
                User.email.like(f"%{q}%") |
                User.name.like(f"%{q}%")
            )
        )
        users = result.scalars().all()
        
        return {
            "search_term": q,
            "results": [
                {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name
                }
                for user in users
            ],
            "count": len(users)
        }
    except Exception as e:
        logger.error(f"User search failed: {e}")
        return {"error": str(e), "results": []}

@admin_router.post("/debug/emergency-user-creation")
async def emergency_user_creation(request: EmergencyUserCreation, db: AsyncSession = Depends(get_db_session)):
    """Emergency: Create or find user for credit assignment"""
    try:
        # First try to find existing user by email
        result = await db.execute(select(User).where(User.email == request.email))
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            logger.info(f"Found existing user: {existing_user.id}")
            return {
                "action": "found_existing",
                "user_id": existing_user.id,
                "email": existing_user.email,
                "name": existing_user.name
            }
        
        # Create new user with minimal schema
        new_user = User(
            email=request.email,
            name=request.name
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        logger.info(f"Created new user: {new_user.id}")
        return {
            "action": "created_new",
            "user_id": new_user.id,
            "email": new_user.email,
            "name": new_user.name
        }
        
    except Exception as e:
        logger.error(f"Emergency user creation failed: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"User creation failed: {e}")

@admin_router.post("/debug/emergency-credit-assignment")
async def emergency_credit_assignment(request: EmergencyCreditAssignment, db: AsyncSession = Depends(get_db_session)):
    """Emergency: Assign credits to correct user"""
    try:
        credits_service = CreditsService(db)
        
        # Ensure customer exists
        await credits_service.ensure_customer(user_id=request.user_id)
        
        # Add credits
        await credits_service.credit_purchase(
            user_id=request.user_id,
            delta=request.credits,
            reason=f"EMERGENCY_FIX: {request.reason}",
            stripe_event_id=request.stripe_event
        )
        
        await db.commit()
        
        # Get new balance
        new_balance = await credits_service.get_balance(user_id=request.user_id)
        
        logger.info(f"Emergency credit assignment successful: {request.credits} credits to {request.user_id}")
        
        return {
            "success": True,
            "user_id": request.user_id,
            "credits_added": request.credits,
            "new_balance": new_balance,
            "reason": request.reason,
            "stripe_event": request.stripe_event,
            "admin_note": request.admin_note
        }
        
    except Exception as e:
        logger.error(f"Emergency credit assignment failed: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Credit assignment failed: {e}")

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
