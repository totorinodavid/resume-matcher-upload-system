"""
BULLETPROOF USER ID SERVICE
- Verwaltet einheitliche User UUIDs
- Mapped alle Auth Provider IDs auf eine einzige UUID
- Löst alle User ID Probleme für immer
"""

from __future__ import annotations
import json
import uuid
from typing import Optional, Dict, Any, List
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.credits import StripeCustomer, CreditLedger
import logging

logger = logging.getLogger(__name__)


class UserResolutionError(Exception):
    """Raised when user cannot be resolved"""
    pass


class UserService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_or_create_user_by_uuid(self, user_uuid: str) -> User:
        """Get user by UUID, create if not exists"""
        try:
            uuid_obj = uuid.UUID(user_uuid)
        except ValueError:
            raise UserResolutionError(f"Invalid UUID format: {user_uuid}")
        
        result = await self.db.execute(
            select(User).where(User.user_uuid == uuid_obj)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            # Create new user with this UUID
            user = User(
                user_uuid=uuid_obj,
                email=f"user_{user_uuid[:8]}@temp.com",  # Temporary email
                name=f"User {user_uuid[:8]}"
            )
            self.db.add(user)
            await self.db.flush()
            logger.info(f"Created new user with UUID: {user_uuid}")
        
        return user

    async def resolve_user_by_any_id(self, identifier: str) -> User:
        """
        UNIVERSAL USER RESOLVER
        Findet User basierend auf JEDER bekannten ID
        """
        logger.info(f"Resolving user by identifier: {identifier}")
        
        # Try UUID first (most common case)
        try:
            uuid_obj = uuid.UUID(identifier)
            result = await self.db.execute(
                select(User).where(User.user_uuid == uuid_obj)
            )
            user = result.scalar_one_or_none()
            if user:
                logger.info(f"Found user by UUID: {identifier}")
                return user
        except ValueError:
            pass  # Not a valid UUID
        
        # Try all auth provider IDs
        result = await self.db.execute(
            select(User).where(
                or_(
                    User.nextauth_user_id == identifier,
                    User.stripe_customer_id == identifier,
                    User.google_user_id == identifier,
                    User.github_user_id == identifier,
                    User.email == identifier
                )
            )
        )
        user = result.scalar_one_or_none()
        if user:
            logger.info(f"Found user by auth provider ID: {identifier}")
            return user
        
        # Check legacy IDs
        result = await self.db.execute(select(User))
        users = result.scalars().all()
        
        for user in users:
            if user.legacy_user_ids:
                try:
                    legacy_ids = json.loads(user.legacy_user_ids)
                    if identifier in legacy_ids:
                        logger.info(f"Found user by legacy ID: {identifier}")
                        return user
                except json.JSONDecodeError:
                    continue
        
        # If no user found, create one
        logger.warning(f"No user found for identifier: {identifier}, creating new user")
        return await self.create_user_for_unknown_id(identifier)

    async def create_user_for_unknown_id(self, identifier: str) -> User:
        """Create new user for unknown identifier"""
        # Generate new UUID
        new_uuid = uuid.uuid4()
        
        user = User(
            user_uuid=new_uuid,
            email=f"user_{identifier[:8]}@temp.com",
            name=f"User {identifier[:8]}",
            legacy_user_ids=json.dumps([identifier])
        )
        
        # Try to determine what type of ID this is
        if "@" in identifier:
            user.email = identifier
        elif "cus_" in identifier:  # Stripe customer
            user.stripe_customer_id = identifier
        else:
            # Could be NextAuth or other provider
            user.nextauth_user_id = identifier
        
        self.db.add(user)
        await self.db.flush()
        
        logger.info(f"Created new user {new_uuid} for unknown identifier: {identifier}")
        return user

    async def link_auth_provider(self, user_uuid: str, provider: str, provider_id: str) -> User:
        """Link auth provider ID to existing user"""
        user = await self.get_or_create_user_by_uuid(user_uuid)
        
        if provider == "nextauth":
            user.nextauth_user_id = provider_id
        elif provider == "stripe":
            user.stripe_customer_id = provider_id
        elif provider == "google":
            user.google_user_id = provider_id
        elif provider == "github":
            user.github_user_id = provider_id
        
        await self.db.flush()
        logger.info(f"Linked {provider} ID {provider_id} to user {user_uuid}")
        return user

    async def migrate_legacy_credits(self, old_user_id: str, new_user_uuid: str) -> bool:
        """Migrate credits from old user ID to new UUID"""
        try:
            # Update StripeCustomer table
            result = await self.db.execute(
                select(StripeCustomer).where(StripeCustomer.user_id == old_user_id)
            )
            stripe_customers = result.scalars().all()
            
            for customer in stripe_customers:
                customer.user_id = new_user_uuid
            
            # Update CreditLedger table
            result = await self.db.execute(
                select(CreditLedger).where(CreditLedger.user_id == old_user_id)
            )
            credit_entries = result.scalars().all()
            
            for entry in credit_entries:
                entry.user_id = new_user_uuid
            
            await self.db.flush()
            logger.info(f"Migrated credits from {old_user_id} to {new_user_uuid}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to migrate credits: {e}")
            return False

    async def get_canonical_user_id(self, any_identifier: str) -> str:
        """
        RETURNS THE ONE TRUE USER UUID
        This is the only ID that should be used everywhere
        """
        user = await self.resolve_user_by_any_id(any_identifier)
        return str(user.user_uuid)
