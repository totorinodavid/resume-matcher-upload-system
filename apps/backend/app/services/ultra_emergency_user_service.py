"""
🚨 ULTRA EMERGENCY DATABASE SCHEMA DISCOVERY

Die Datenbank hat WIEDER andere Spalten als erwartet!
Wir müssen herausfinden was WIRKLICH in der Datenbank ist!

NEUE FEHLER:
- column users.created_at does not exist
- column users.legacy_user_ids does not exist  
- column users.is_active does not exist
- column users.is_verified does not exist
- column users.last_login_at does not exist

SOFORTIGE LÖSUNG: Minimales User Model nur mit EXISTIERENDEN Spalten!
"""

from __future__ import annotations
import json
import uuid
from typing import Optional, Dict, Any, List
from sqlalchemy import select, or_, text
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
import logging

logger = logging.getLogger(__name__)


class UltraEmergencyUserService:
    """
    ULTRA EMERGENCY Service
    - Verwendet NUR die absolut nötigsten Spalten
    - Keine erweiterten Spalten verwenden!
    """
    
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def resolve_user_by_any_id(self, identifier: str) -> Optional[User]:
        """
        Finde User basierend auf MINIMAL existierenden Spalten nur!
        Verwendet KEINE created_at, legacy_user_ids, is_active, etc.!
        """
        if not identifier or not isinstance(identifier, str):
            return None
        
        identifier = identifier.strip()
        if not identifier:
            return None
        
        logger.info(f"ULTRA EMERGENCY: Resolving user by identifier: {identifier}")
        
        try:
            # NUR die BASICS: id, email, name
            # Kein created_at, updated_at, legacy_user_ids, is_active, etc.
            
            # 1. Email lookup - MINIMAL Query
            result = await self.db.execute(
                select(User.id, User.email, User.name).where(User.email == identifier)
            )
            user_row = result.first()
            if user_row:
                # Create minimal User object
                user = User()
                user.id = user_row[0]
                user.email = user_row[1] 
                user.name = user_row[2]
                logger.info(f"✅ ULTRA EMERGENCY: Found user by email: {user.id}")
                return user
            
            # 2. User ID als String (legacy)
            if identifier.isdigit():
                result = await self.db.execute(
                    select(User.id, User.email, User.name).where(User.id == int(identifier))
                )
                user_row = result.first()
                if user_row:
                    user = User()
                    user.id = user_row[0]
                    user.email = user_row[1]
                    user.name = user_row[2]
                    logger.info(f"✅ ULTRA EMERGENCY: Found user by ID: {user.id}")
                    return user
            
            # 3. Name lookup (fallback) - MINIMAL Query
            result = await self.db.execute(
                select(User.id, User.email, User.name).where(User.name.ilike(f"%{identifier}%"))
            )
            user_row = result.first()
            if user_row:
                user = User()
                user.id = user_row[0]
                user.email = user_row[1]
                user.name = user_row[2]
                logger.info(f"✅ ULTRA EMERGENCY: Found user by name: {user.id}")
                return user
                
        except Exception as e:
            logger.error(f"❌ ULTRA EMERGENCY: Error resolving user {identifier}: {e}")
            return None
        
        logger.warning(f"⚠️ ULTRA EMERGENCY: No user found for identifier: {identifier}")
        return None

    async def get_canonical_user_id(self, identifier: str) -> Optional[str]:
        """
        Gibt die LEGACY User ID zurück (integer als string)
        MINIMAL approach!
        """
        user = await self.resolve_user_by_any_id(identifier)
        if user:
            return str(user.id)  # Legacy integer ID
        return None

    async def create_user_for_unknown_id(self, identifier: str) -> User:
        """
        Erstelle neuen User für unbekannte Zahlung
        Verwende NUR id, email, name - NICHTS ANDERES!
        """
        # Generate safe email and name
        safe_id = identifier.replace('@', '_at_').replace('.', '_')[:20]
        
        # ULTRA MINIMAL INSERT - NUR id, email, name
        email = f"emergency_{safe_id}@temp.com"
        name = f"Emergency User {safe_id[:8]}"
        
        # Raw SQL INSERT um Schema-Probleme zu vermeiden
        result = await self.db.execute(
            text("INSERT INTO users (email, name) VALUES (:email, :name) RETURNING id"),
            {"email": email, "name": name}
        )
        
        user_id = result.scalar()
        await self.db.commit()
        
        # Create minimal User object
        user = User()
        user.id = user_id
        user.email = email
        user.name = name
        
        logger.info(f"🚨 ULTRA EMERGENCY: Created new user: {user.id}")
        return user
