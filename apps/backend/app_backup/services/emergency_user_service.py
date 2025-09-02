"""
🚨 EMERGENCY DATABASE SCHEMA FIX

Das User Model hat neue Spalten definiert die in der Datenbank NICHT existieren!
Aktueller Fehler: column users.user_uuid does not exist

SOFORTIGE LÖSUNG: Legacy User Service der mit der aktuellen DB Schema arbeitet
"""

from __future__ import annotations
import json
import uuid
from typing import Optional, Dict, Any, List
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User  # Verwende das existierende Model
import logging

logger = logging.getLogger(__name__)


class EmergencyUserService:
    """
    EMERGENCY Service der mit der AKTUELLEN Datenbank funktioniert
    - Keine user_uuid Spalte verwenden!
    - Nutze nur existierende Spalten
    """
    
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def resolve_user_by_any_id(self, identifier: str) -> Optional[User]:
        """
        Finde User basierend auf EXISTIERENDEN Spalten nur!
        Verwendet NICHT user_uuid weil diese Spalte nicht existiert!
        """
        if not identifier or not isinstance(identifier, str):
            return None
        
        identifier = identifier.strip()
        if not identifier:
            return None
        
        logger.info(f"EMERGENCY: Resolving user by identifier: {identifier}")
        
        try:
            # Suche basierend auf existierenden Spalten
            # 1. Email
            result = await self.db.execute(
                select(User).where(User.email == identifier)
            )
            user = result.scalar_one_or_none()
            if user:
                logger.info(f"✅ EMERGENCY: Found user by email: {user.id}")
                return user
            
            # 2. User ID als String (legacy)
            if identifier.isdigit():
                result = await self.db.execute(
                    select(User).where(User.id == int(identifier))
                )
                user = result.scalar_one_or_none()
                if user:
                    logger.info(f"✅ EMERGENCY: Found user by ID: {user.id}")
                    return user
            
            # 3. Name lookup (fallback)
            result = await self.db.execute(
                select(User).where(User.name.ilike(f"%{identifier}%"))
            )
            user = result.scalar_one_or_none()
            if user:
                logger.info(f"✅ EMERGENCY: Found user by name: {user.id}")
                return user
                
        except Exception as e:
            logger.error(f"❌ EMERGENCY: Error resolving user {identifier}: {e}")
            return None
        
        logger.warning(f"⚠️ EMERGENCY: No user found for identifier: {identifier}")
        return None

    async def get_canonical_user_id(self, identifier: str) -> Optional[str]:
        """
        Gibt die LEGACY User ID zurück (integer als string)
        NICHT user_uuid weil diese Spalte nicht existiert!
        """
        user = await self.resolve_user_by_any_id(identifier)
        if user:
            return str(user.id)  # Legacy integer ID
        return None

    async def create_user_for_unknown_id(self, identifier: str) -> User:
        """
        Erstelle neuen User für unbekannte Zahlung
        Verwende NUR existierende Spalten!
        """
        # Generate safe email and name
        safe_id = identifier.replace('@', '_at_').replace('.', '_')[:20]
        
        user = User(
            email=f"emergency_{safe_id}@temp.com",
            name=f"Emergency User {safe_id[:8]}"
        )
        
        self.db.add(user)
        await self.db.flush()
        
        logger.info(f"🚨 EMERGENCY: Created new user: {user.id}")
        return user
