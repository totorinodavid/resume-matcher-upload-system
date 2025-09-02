#!/usr/bin/env python3
"""
🚨 EMERGENCY PRODUCTION USER RESOLVER FIX

This creates a version of the user resolver that works with production
schema that might not have credits_balance column yet.
"""

import os
import sys

def create_production_safe_user_resolver():
    """Create a user resolver that works with current production schema."""
    
    content = '''"""
PRODUCTION-SAFE User Resolver for Emergency Hotfix

This version works with existing production schema and gracefully handles
missing credits_balance column until schema is updated.
"""

import logging
import re
import uuid
from typing import Optional, Union, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError, NoResultFound

logger = logging.getLogger(__name__)


def is_email(identifier: str) -> bool:
    """Check if identifier is an email address."""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, identifier))


def is_uuid(identifier: str) -> bool:
    """Check if identifier is a valid UUID."""
    try:
        uuid.UUID(identifier)
        return True
    except (ValueError, TypeError):
        return False


def is_integer_id(identifier: str) -> bool:
    """Check if identifier is a valid integer ID."""
    try:
        int(identifier)
        return True
    except (ValueError, TypeError):
        return False


def is_placeholder(identifier: str) -> bool:
    """Check if identifier is a placeholder like '<email>' or '<phone>'."""
    return bool(re.match(r'^<[^>]+>$', identifier))


async def find_user_safe(db: AsyncSession, identifier: str) -> Optional[Any]:
    """
    PRODUCTION-SAFE user finder that works with existing schema.
    Only queries columns that definitely exist in production.
    """
    try:
        # Import the User model
        from app.models.user import User
        
        # Check if credits_balance column exists by trying to access it
        try:
            # Try with credits_balance first (new schema)
            if is_email(identifier):
                result = await db.execute(
                    select(User).where(User.email == identifier)
                )
            elif is_integer_id(identifier):
                result = await db.execute(
                    select(User).where(User.id == int(identifier))
                )
            else:
                # For UUID or other identifiers, try email field
                result = await db.execute(
                    select(User).where(User.email == identifier)
                )
            
            return result.scalar_one_or_none()
            
        except SQLAlchemyError as e:
            # If error mentions credits_balance, try without it
            if "credits_balance" in str(e):
                logger.warning(f"credits_balance column not found, using basic query: {e}")
                
                # Use raw SQL that only queries existing columns
                if is_email(identifier):
                    result = await db.execute(text("""
                        SELECT id, email, name 
                        FROM users 
                        WHERE email = :identifier
                    """), {"identifier": identifier})
                elif is_integer_id(identifier):
                    result = await db.execute(text("""
                        SELECT id, email, name 
                        FROM users 
                        WHERE id = :identifier
                    """), {"identifier": int(identifier)})
                else:
                    result = await db.execute(text("""
                        SELECT id, email, name 
                        FROM users 
                        WHERE email = :identifier
                    """), {"identifier": identifier})
                
                row = result.fetchone()
                if row:
                    # Create a simple user-like object
                    class SimpleUser:
                        def __init__(self, id, email, name):
                            self.id = id
                            self.email = email
                            self.name = name
                            self.credits_balance = 0  # Default for compatibility
                    
                    return SimpleUser(row.id, row.email, row.name)
                return None
            else:
                raise  # Re-raise if not related to credits_balance
                
    except Exception as e:
        logger.error(f"Error finding user {identifier}: {e}")
        return None


async def resolve_user_safe(db: AsyncSession, identifier: str) -> Optional[Any]:
    """
    PRODUCTION-SAFE user resolver with fallback strategies.
    """
    # Skip obviously invalid identifiers
    if not identifier or is_placeholder(identifier):
        return None
    
    # Skip non-user identifiers
    skip_patterns = [
        r'^\d{4}-\d{2}-\d{2}T',  # ISO timestamps
        r'^price_',              # Stripe price IDs
        r'^bulletproof_',        # System identifiers
        r'^\d+\.\d+$',          # Version numbers like "2.0"
        r'^(small|medium|large)$',  # Plan names
    ]
    
    for pattern in skip_patterns:
        if re.match(pattern, identifier):
            return None
    
    logger.info(f"PRODUCTION-SAFE: Resolving user by identifier: {identifier}")
    
    try:
        return await find_user_safe(db, identifier)
    except Exception as e:
        logger.error(f"Error resolving user {identifier}: {e}")
        return None


async def resolve_or_create_user_safe(
    db: AsyncSession, 
    identifier: str, 
    fallback_email: Optional[str] = None,
    fallback_name: Optional[str] = None
) -> Optional[Any]:
    """
    PRODUCTION-SAFE resolve or create user with emergency fallback.
    """
    # Try to resolve existing user first
    user = await resolve_user_safe(db, identifier)
    if user:
        return user
    
    # If no user found and we have fallback data, create new user
    if fallback_email and not is_placeholder(fallback_email):
        try:
            logger.info(f"PRODUCTION-SAFE: Creating/finding user for {identifier}")
            
            # Use raw SQL for creation to avoid model issues
            result = await db.execute(text("""
                INSERT INTO users (email, name) 
                VALUES (:email, :name) 
                ON CONFLICT (email) DO UPDATE SET name = :name
                RETURNING id, email, name
            """), {
                "email": fallback_email,
                "name": fallback_name or f"Emergency User {identifier[:8]}"
            })
            
            row = result.fetchone()
            if row:
                # Create a simple user-like object
                class SimpleUser:
                    def __init__(self, id, email, name):
                        self.id = id
                        self.email = email
                        self.name = name
                        self.credits_balance = 0  # Default for compatibility
                
                user = SimpleUser(row.id, row.email, row.name)
                await db.commit()
                logger.info(f"✅ Created/found user: {user.id}")
                return user
            
        except Exception as e:
            logger.error(f"❌ User creation failed: {e}")
            await db.rollback()
    
    return None


async def add_credits_safe(db: AsyncSession, user_id: int, credits: int) -> bool:
    """
    PRODUCTION-SAFE credit addition that works with or without credits_balance column.
    """
    try:
        # Try to add credits using new schema
        await db.execute(text("""
            UPDATE users 
            SET credits_balance = COALESCE(credits_balance, 0) + :credits 
            WHERE id = :user_id
        """), {"credits": credits, "user_id": user_id})
        
        await db.commit()
        logger.info(f"✅ Added {credits} credits to user {user_id}")
        return True
        
    except SQLAlchemyError as e:
        if "credits_balance" in str(e):
            # Column doesn't exist yet, log but don't fail
            logger.warning(f"⚠️  credits_balance column not ready, credits not added: {credits} for user {user_id}")
            await db.rollback()
            return False
        else:
            logger.error(f"❌ Failed to add credits: {e}")
            await db.rollback()
            return False
    except Exception as e:
        logger.error(f"❌ Unexpected error adding credits: {e}")
        await db.rollback()
        return False


# Export the safe functions
__all__ = [
    'find_user_safe',
    'resolve_user_safe', 
    'resolve_or_create_user_safe',
    'add_credits_safe',
    'is_email',
    'is_uuid',
    'is_integer_id',
    'is_placeholder'
]
'''
    
    # Write to the backend directory
    backend_path = os.path.join("apps", "backend", "app", "db")
    os.makedirs(backend_path, exist_ok=True)
    
    safe_resolver_path = os.path.join(backend_path, "resolver_safe.py")
    
    with open(safe_resolver_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Created production-safe user resolver: {safe_resolver_path}")
    return safe_resolver_path


def create_emergency_webhook_fix():
    """Create an emergency webhook handler that uses the safe resolver."""
    
    content = '''"""
🚨 EMERGENCY WEBHOOK HANDLER for Production

This version uses the production-safe resolver and handles missing schema gracefully.
"""

import logging
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.resolver_safe import (
    resolve_user_safe, 
    resolve_or_create_user_safe, 
    add_credits_safe,
    is_placeholder
)

logger = logging.getLogger(__name__)


async def handle_checkout_completed_safe(
    db: AsyncSession,
    event_id: str,
    session_data: Dict[str, Any],
    request_id: str
) -> bool:
    """
    PRODUCTION-SAFE checkout completion handler.
    Works with existing schema and handles missing columns gracefully.
    """
    try:
        logger.info(f"🛡️  SAFE: Processing checkout completion for event {event_id}")
        
        # Extract data from session
        customer_id = session_data.get('customer')
        metadata = session_data.get('metadata', {})
        payment_status = session_data.get('payment_status')
        
        # Only process paid sessions
        if payment_status != 'paid':
            logger.warning(f"⚠️  SAFE: Session not paid: {payment_status}")
            return False
        
        # Extract credits from metadata
        credits_str = metadata.get('credits', '0')
        try:
            credits = int(credits_str)
        except (ValueError, TypeError):
            logger.error(f"❌ SAFE: Invalid credits value: {credits_str}")
            return False
        
        if credits <= 0:
            logger.warning(f"⚠️  SAFE: No credits to add: {credits}")
            return True  # Not an error, just nothing to do
        
        # Get user identifiers from metadata
        user_identifiers = [
            metadata.get('user_id'),
            metadata.get('authenticated_user'),
            metadata.get('nextauth_user_id'),
            metadata.get('primary_user_id'),
            metadata.get('session_email'),
        ]
        
        # Filter out invalid identifiers
        valid_identifiers = [
            uid for uid in user_identifiers 
            if uid and not is_placeholder(uid)
        ]
        
        if not valid_identifiers:
            logger.error(f"❌ SAFE: No valid user identifiers found in metadata")
            return False
        
        # Try to resolve user using safe method
        user = None
        for identifier in valid_identifiers:
            user = await resolve_user_safe(db, identifier)
            if user:
                logger.info(f"✅ SAFE: Found user {user.id} using identifier: {identifier}")
                break
        
        # If no user found, try to create one
        if not user:
            fallback_email = metadata.get('session_email')
            fallback_name = metadata.get('session_name', 'Emergency User')
            
            if fallback_email and not is_placeholder(fallback_email):
                user = await resolve_or_create_user_safe(
                    db, 
                    valid_identifiers[0],
                    fallback_email=fallback_email,
                    fallback_name=fallback_name
                )
        
        if not user:
            logger.error(f"❌ SAFE: Could not resolve or create user")
            return False
        
        # Add credits using safe method
        success = await add_credits_safe(db, user.id, credits)
        
        if success:
            logger.info(f"🎉 SAFE: Successfully added {credits} credits to user {user.id}")
        else:
            logger.warning(f"⚠️  SAFE: Credits not added (schema not ready), but user resolved: {user.id}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ SAFE: Checkout processing failed: {e}")
        await db.rollback()
        return False


# Export the safe handler
__all__ = ['handle_checkout_completed_safe']
'''
    
    # Write to the backend directory  
    backend_path = os.path.join("apps", "backend", "app", "webhooks")
    os.makedirs(backend_path, exist_ok=True)
    
    safe_webhook_path = os.path.join(backend_path, "stripe_checkout_safe.py")
    
    with open(safe_webhook_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Created production-safe webhook handler: {safe_webhook_path}")
    return safe_webhook_path


def main():
    """Create all production-safe components."""
    print("🚨 Creating emergency production-safe components...")
    
    resolver_path = create_production_safe_user_resolver()
    webhook_path = create_emergency_webhook_fix()
    
    print("\n✅ Emergency production-safe components created:")
    print(f"   - Safe User Resolver: {resolver_path}")
    print(f"   - Safe Webhook Handler: {webhook_path}")
    print("\n📋 Next steps:")
    print("1. Run the emergency_production_hotfix.py to fix the schema")
    print("2. Update the webhook router to use the safe handler")
    print("3. Test the production deployment")


if __name__ == "__main__":
    main()
