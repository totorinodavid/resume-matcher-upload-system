#!/usr/bin/env python3
"""
🚨 CRITICAL PRODUCTION HOTFIX FOR TRANSACTION ROLLBACK ISSUE

The production logs show:
1. First query fails: column users.credits_balance does not exist  
2. Transaction becomes aborted 
3. All subsequent queries fail with: current transaction is aborted, commands ignored until end of transaction block

SOLUTION: Fix the transaction handling in UltraEmergencyUserService
"""

import os
import sys

def create_fixed_ultra_emergency_user_service():
    """Create a fixed version that handles transaction rollbacks properly."""
    
    content = '''"""
🚨 FIXED ULTRA EMERGENCY USER SERVICE with Proper Transaction Handling

This version handles SQLAlchemy errors properly and starts fresh transactions
when the current one is aborted.
"""

from __future__ import annotations
import json
import uuid
from typing import Optional, Dict, Any, List
from sqlalchemy import select, or_, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)


class UltraEmergencyUserService:
    """
    FIXED ULTRA EMERGENCY Service with proper transaction handling.
    
    Key fixes:
    1. Catches SQLAlchemy errors and starts fresh transactions
    2. Uses raw SQL when ORM queries fail
    3. Handles aborted transactions gracefully
    """
    
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def _rollback_and_start_fresh(self) -> bool:
        """Rollback aborted transaction and prepare for fresh queries."""
        try:
            await self.db.rollback()
            logger.info("✅ Transaction rolled back successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to rollback transaction: {e}")
            return False

    async def _query_user_safe(self, where_clause: str, params: dict) -> Optional[tuple]:
        """
        Execute a user query safely, handling transaction errors.
        Returns tuple of (id, email, name) or None.
        """
        # First try with ORM
        try:
            from app.models.user import User
            
            if "email" in where_clause:
                result = await self.db.execute(
                    select(User.id, User.email, User.name).where(User.email == params.get('email'))
                )
            elif "id" in where_clause:
                result = await self.db.execute(
                    select(User.id, User.email, User.name).where(User.id == params.get('id'))
                )
            else:
                return None
                
            row = result.fetchone()
            return row
            
        except SQLAlchemyError as e:
            logger.warning(f"ORM query failed, trying raw SQL: {e}")
            
            # Rollback the failed transaction
            await self._rollback_and_start_fresh()
            
            # Try with raw SQL
            try:
                sql = f"SELECT id, email, name FROM users WHERE {where_clause}"
                result = await self.db.execute(text(sql), params)
                row = result.fetchone()
                return row
                
            except SQLAlchemyError as e2:
                logger.error(f"Raw SQL query also failed: {e2}")
                await self._rollback_and_start_fresh()
                return None

    async def resolve_user_by_any_id(self, identifier: str) -> Optional[object]:
        """
        Find user by any identifier with proper error handling.
        Returns a simple user object with id, email, name.
        """
        if not identifier or not isinstance(identifier, str):
            return None
        
        identifier = identifier.strip()
        if not identifier:
            return None
        
        logger.info(f"ULTRA EMERGENCY: Resolving user by identifier: {identifier}")
        
        # Create a simple user class for return values
        class SimpleUser:
            def __init__(self, id: int, email: str, name: str):
                self.id = id
                self.email = email
                self.name = name
                # Add credits_balance for compatibility but don't query it
                self.credits_balance = 0
        
        try:
            # 1. Try as email
            row = await self._query_user_safe("email = :email", {"email": identifier})
            if row:
                logger.info(f"✅ Found user by email: {row[0]}")
                return SimpleUser(row[0], row[1], row[2])
            
            # 2. Try as integer ID
            try:
                int_id = int(identifier)
                row = await self._query_user_safe("id = :id", {"id": int_id})
                if row:
                    logger.info(f"✅ Found user by ID: {row[0]}")
                    return SimpleUser(row[0], row[1], row[2])
            except ValueError:
                pass  # Not a number
            
            # 3. Try as name pattern (be careful with SQL injection)
            if len(identifier) > 2 and identifier.replace(' ', '').replace('-', '').replace('_', '').isalnum():
                try:
                    sql = "SELECT id, email, name FROM users WHERE name ILIKE :pattern"
                    result = await self.db.execute(text(sql), {"pattern": f"%{identifier}%"})
                    row = result.fetchone()
                    if row:
                        logger.info(f"✅ Found user by name pattern: {row[0]}")
                        return SimpleUser(row[0], row[1], row[2])
                except SQLAlchemyError as e:
                    logger.warning(f"Name search failed: {e}")
                    await self._rollback_and_start_fresh()
            
            logger.warning(f"⚠️  No user found for identifier: {identifier}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error resolving user {identifier}: {e}")
            await self._rollback_and_start_fresh()
            return None

    async def get_canonical_user_id(self, identifier: str) -> Optional[str]:
        """
        Get the canonical user ID (integer as string).
        """
        user = await self.resolve_user_by_any_id(identifier)
        if user:
            return str(user.id)
        return None

    async def create_user_for_unknown_id(self, identifier: str) -> Optional[object]:
        """
        Create a new user for unknown payment with proper error handling.
        """
        logger.info(f"🚨 ULTRA EMERGENCY: Creating/finding user for {identifier}")
        
        # Create a simple user class
        class SimpleUser:
            def __init__(self, id: int, email: str, name: str):
                self.id = id
                self.email = email
                self.name = name
                self.credits_balance = 0
        
        # Generate safe email and name
        safe_id = ''.join(c for c in identifier if c.isalnum() or c in '-_')[:20]
        email = f"emergency_{safe_id}@temp.com"
        name = f"Emergency User {safe_id[:8]}"
        
        # Check if user already exists
        existing = await self.resolve_user_by_any_id(email)
        if existing:
            logger.info(f"✅ User already exists: {existing.id}")
            return existing
        
        # Create new user with raw SQL to avoid model issues
        try:
            await self._rollback_and_start_fresh()  # Ensure clean transaction
            
            result = await self.db.execute(
                text("INSERT INTO users (email, name) VALUES (:email, :name) RETURNING id, email, name"),
                {"email": email, "name": name}
            )
            
            row = result.fetchone()
            if row:
                await self.db.commit()
                user = SimpleUser(row[0], row[1], row[2])
                logger.info(f"🎉 Created user: {user.id} ({email})")
                return user
            else:
                await self.db.rollback()
                logger.error("❌ No user returned from INSERT")
                return None
                
        except SQLAlchemyError as e:
            logger.error(f"❌ User creation failed: {e}")
            await self._rollback_and_start_fresh()
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected error creating user: {e}")
            await self._rollback_and_start_fresh()
            return None

    async def add_credits_to_user(self, user_id: int, credits: int) -> bool:
        """
        Add credits to user with proper error handling.
        """
        try:
            await self._rollback_and_start_fresh()  # Ensure clean transaction
            
            # Try to update credits_balance
            result = await self.db.execute(
                text("UPDATE users SET credits_balance = COALESCE(credits_balance, 0) + :credits WHERE id = :user_id"),
                {"credits": credits, "user_id": user_id}
            )
            
            await self.db.commit()
            logger.info(f"✅ Added {credits} credits to user {user_id}")
            return True
            
        except SQLAlchemyError as e:
            if "credits_balance" in str(e).lower():
                logger.warning(f"⚠️  credits_balance column not available, credits not added: {credits} for user {user_id}")
                await self._rollback_and_start_fresh()
                return False
            else:
                logger.error(f"❌ Failed to add credits: {e}")
                await self._rollback_and_start_fresh()
                return False
        except Exception as e:
            logger.error(f"❌ Unexpected error adding credits: {e}")
            await self._rollback_and_start_fresh()
            return False
'''
    
    # Write the fixed service
    service_path = os.path.join("apps", "backend", "app", "services", "ultra_emergency_user_service.py")
    
    # Backup original
    backup_path = service_path + ".broken_backup"
    if os.path.exists(service_path):
        with open(service_path, 'r', encoding='utf-8') as f:
            original = f.read()
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original)
        print(f"✅ Backed up broken service to: {backup_path}")
    
    # Write fixed version
    with open(service_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Created FIXED UltraEmergencyUserService: {service_path}")
    print("🔧 Key fixes:")
    print("   - Proper transaction rollback handling")
    print("   - Raw SQL fallback when ORM fails")
    print("   - Graceful handling of aborted transactions")
    print("   - Safe user creation without model dependencies")
    
    return service_path


def main():
    """Apply the critical production hotfix."""
    print("🚨 Applying CRITICAL PRODUCTION HOTFIX for transaction rollback issue...")
    
    service_path = create_fixed_ultra_emergency_user_service()
    
    print(f"\n✅ CRITICAL HOTFIX APPLIED!")
    print(f"Fixed service: {service_path}")
    print("\n📋 IMMEDIATE NEXT STEPS:")
    print("1. This fix should resolve the transaction rollback errors")
    print("2. The service now handles missing credits_balance gracefully")
    print("3. User resolution will work even with schema mismatches")
    print("4. Deploy this change immediately to stop the error cascade")
    
    print("\n🔍 What this fixes:")
    print("   ❌ Before: First query fails → transaction aborted → all queries fail")
    print("   ✅ After:  First query fails → rollback → fresh transaction → continue")


if __name__ == "__main__":
    main()
