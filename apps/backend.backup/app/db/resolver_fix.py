# ------------------------------------------------------------------
# 4) PYTHON: Robuster User-Resolver (Email/UUID/Placeholder)
# ------------------------------------------------------------------
# Drop-in-Ready. Ersetzt fehleranfällige WHERE users.email = $1-Variante.
# Erkennt Email vs. UUID, ignoriert Platzhalter wie "<email>".

import re
from uuid import UUID
from typing import Optional, Any, Dict
from sqlalchemy import select, or_, cast, String, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
import logging

from ..db.session_patterns import safe_rollback

logger = logging.getLogger(__name__)

EMAIL_RE = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")


def is_uuid(v: str) -> bool:
    """Check if string is a valid UUID."""
    try:
        UUID(str(v))
        return True
    except (ValueError, TypeError):
        return False


def is_email(v: str) -> bool:
    """Check if string is a valid email address."""
    if not v or not isinstance(v, str):
        return False
    return bool(EMAIL_RE.fullmatch(str(v).strip()))


def is_placeholder(v: str) -> bool:
    """Check if string is a placeholder value that should be ignored."""
    if not v or not isinstance(v, str):
        return True
    s = str(v).strip()
    return (
        not s or 
        s.startswith("<") or 
        s.endswith(">") or
        s in ("null", "None", "undefined", "test@example.com", "user@example.com")
    )


def is_integer_id(v: str) -> bool:
    """Check if string represents a valid integer ID."""
    try:
        int(str(v))
        return True
    except (ValueError, TypeError):
        return False


async def find_user(session: AsyncSession, UserModel: Any, identifier: str) -> Optional[Any]:
    """
    Find user by identifier using smart detection of identifier type.
    
    Supports:
    - Email addresses 
    - UUID strings
    - Integer IDs
    - Fallback to email OR UUID/ID search
    
    Args:
        session: Database session
        UserModel: SQLAlchemy User model class
        identifier: User identifier to search for
        
    Returns:
        User instance if found, None otherwise
        
    Raises:
        SQLAlchemyError: On database errors (after automatic rollback)
    """
    if is_placeholder(identifier):
        logger.debug(f"Ignoring placeholder identifier: {identifier}")
        return None
        
    ident = str(identifier).strip()
    logger.debug(f"Finding user by identifier: {ident}")

    try:
        if is_email(ident):
            # Email lookup - most common case
            logger.debug(f"Searching by email: {ident}")
            q = select(UserModel).where(UserModel.email == ident)
            
        elif is_uuid(ident):
            # UUID lookup - if User model uses UUID primary key
            logger.debug(f"Searching by UUID: {ident}")
            if hasattr(UserModel, 'user_uuid'):
                q = select(UserModel).where(UserModel.user_uuid == UUID(ident))
            else:
                # Fallback to string comparison if no UUID field
                q = select(UserModel).where(cast(UserModel.id, String) == ident)
                
        elif is_integer_id(ident):
            # Integer ID lookup - legacy support
            logger.debug(f"Searching by integer ID: {ident}")
            q = select(UserModel).where(UserModel.id == int(ident))
            
        else:
            # Fallback: try both email and ID string comparison
            logger.debug(f"Fallback search for: {ident}")
            q = select(UserModel).where(
                or_(
                    UserModel.email == ident,
                    cast(UserModel.id, String) == ident
                )
            )

        result = await session.execute(q)
        user = result.scalar_one_or_none()
        
        if user:
            logger.info(f"✅ Found user {user.id} by identifier: {ident}")
        else:
            logger.debug(f"No user found for identifier: {ident}")
            
        return user
        
    except SQLAlchemyError as e:
        logger.error(f"Database error finding user by {ident}: {e}", exc_info=True)
        await safe_rollback(session)
        raise


async def resolve_user(
    session: AsyncSession, 
    UserModel: Any, 
    meta: Optional[Dict[str, Any]], 
    stripe_session_obj: Optional[Any] = None
) -> Optional[Any]:
    """
    Resolve user from multiple possible sources with priority ordering.
    
    Priority order:
    1. Stripe checkout session customer email (most reliable)
    2. Metadata session_email
    3. Metadata user_id
    4. Metadata authenticated_user  
    5. Metadata primary_user_id
    6. Metadata nextauth_user_id
    
    Args:
        session: Database session
        UserModel: SQLAlchemy User model class  
        meta: Metadata dictionary from webhook/request
        stripe_session_obj: Optional Stripe session object
        
    Returns:
        User instance if found, None otherwise
    """
    logger.debug("Starting user resolution process")
    
    # 1) Checkout-Session customer email has highest priority
    email = None
    if stripe_session_obj and hasattr(stripe_session_obj, "customer_details"):
        customer_details = getattr(stripe_session_obj, "customer_details", None)
        if customer_details:
            email = getattr(customer_details, "email", None)
    
    if email and not is_placeholder(email):
        logger.debug(f"Trying Stripe customer email: {email}")
        u = await find_user(session, UserModel, email)
        if u:
            logger.info(f"✅ Resolved user via Stripe customer email: {u.id}")
            return u

    # 2) Try metadata candidates in order of reliability
    meta = meta or {}
    candidates = [
        ("session_email", meta.get("session_email")),
        ("user_id", meta.get("user_id")), 
        ("authenticated_user", meta.get("authenticated_user")),
        ("primary_user_id", meta.get("primary_user_id")),
        ("nextauth_user_id", meta.get("nextauth_user_id")),
    ]
    
    for source, candidate in candidates:
        if not candidate or is_placeholder(candidate):
            continue
            
        logger.debug(f"Trying {source}: {candidate}")
        u = await find_user(session, UserModel, candidate)
        if u:
            logger.info(f"✅ Resolved user via {source}: {u.id}")
            return u
    
    logger.warning("❌ Could not resolve user from any source")
    return None


async def resolve_or_create_user(
    session: AsyncSession,
    UserModel: Any, 
    meta: Optional[Dict[str, Any]],
    stripe_session_obj: Optional[Any] = None,
    auto_create: bool = False
) -> Optional[Any]:
    """
    Resolve user or optionally create new user if not found.
    
    Args:
        session: Database session
        UserModel: SQLAlchemy User model class
        meta: Metadata dictionary
        stripe_session_obj: Optional Stripe session object  
        auto_create: Whether to create user if not found
        
    Returns:
        User instance (existing or newly created), None if not found and auto_create=False
    """
    # Try to resolve existing user first
    user = await resolve_user(session, UserModel, meta, stripe_session_obj)
    if user:
        return user
    
    if not auto_create:
        return None
        
    # Create new user from available information
    logger.info("Creating new user from webhook data")
    
    # Get email from best available source
    email = None
    name = None
    
    # Try Stripe customer details first
    if stripe_session_obj and hasattr(stripe_session_obj, "customer_details"):
        customer_details = getattr(stripe_session_obj, "customer_details", None)
        if customer_details:
            email = getattr(customer_details, "email", None)
            name = getattr(customer_details, "name", None)
    
    # Fallback to metadata
    if not email:
        email = (meta or {}).get("session_email")
    if not name:
        name = (meta or {}).get("session_name") or (meta or {}).get("user_name")
    
    # Validate email
    if not email or is_placeholder(email) or not is_email(email):
        logger.error("Cannot create user without valid email")
        return None
    
    # Generate safe name if needed
    if not name or is_placeholder(name):
        name = f"User {email.split('@')[0]}"
    
    try:
        # Use upsert pattern to handle race conditions
        from sqlalchemy.dialects.postgresql import insert
        
        stmt = (
            insert(UserModel)
            .values(email=email, name=name[:100])  # Truncate name to safe length
            .on_conflict_do_update(
                index_elements=[UserModel.email],
                set_={"name": name[:100]}  # Update name if email exists
            )
            .returning(UserModel.id)
        )
        
        result = await session.execute(stmt)
        user_id = result.scalar_one()
        
        # Fetch the complete user object
        user = await find_user(session, UserModel, email)
        
        if user:
            logger.info(f"✅ Created/updated user {user.id} with email: {email}")
            return user
        else:
            logger.error(f"Failed to fetch user after upsert for email: {email}")
            return None
            
    except SQLAlchemyError as e:
        logger.error(f"Failed to create user for {email}: {e}", exc_info=True)
        await safe_rollback(session)
        raise
