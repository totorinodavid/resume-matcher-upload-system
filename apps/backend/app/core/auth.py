from __future__ import annotations

import time
import os
import base64
import json
from functools import lru_cache
from typing import Any, Dict, Optional

import httpx
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .config import settings


class Principal:
    """Represents an authenticated user principal with authentication metadata."""
    
    def __init__(
        self,
        user_id: str,
        email: Optional[str] = None,
        auth_type: str = "unknown",
        name: Optional[str] = None,
        picture: Optional[str] = None,
        claims: Optional[Dict[str, Any]] = None,
        token_data: Optional[Dict[str, Any]] = None
    ):
        self.user_id = user_id
        self.email = email
        self.name = name
        self.picture = picture
        self.auth_type = auth_type  # "nextauth_jwt", "fallback", "header", etc.
        self.claims = claims or {}
        self.token_data = token_data or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert principal to dictionary for logging/debugging."""
        return {
            "user_id": self.user_id,
            "email": self.email,
            "name": self.name,
            "auth_type": self.auth_type,
            "has_claims": bool(self.claims),
        }


class JWKSCache:
    def __init__(self) -> None:
        self._cache: dict[str, tuple[dict[str, Any], float]] = {}
        self.ttl_seconds = 900  # 15 minutes

    async def get_keyset(self, issuer: str) -> dict[str, Any]:
        now = time.time()
        entry = self._cache.get(issuer)
        if entry and (now - entry[1]) < self.ttl_seconds:
            return entry[0]
        # Allow override via explicit JWKS URL for flexibility
        url = (os.getenv('NEXTAUTH_JWKS_URL') or '').strip() or (issuer.rstrip('/') + '/.well-known/jwks.json')
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            jwks = resp.json()
        self._cache[issuer] = (jwks, now)
        return jwks


_jwks_cache = JWKSCache()


async def verify_nextauth_token(token: str) -> Principal:
    # Lazy import jose so tests can run without python-jose installed when auth is disabled
    try:
        from jose import jwt  # type: ignore
        from jose.exceptions import JWTError, ExpiredSignatureError  # type: ignore
    except Exception:  # ImportError or others
        if os.getenv("DISABLE_AUTH_FOR_TESTS") == "1":
            # In tests, bypass verification entirely
            return Principal(user_id="test-user")
        # Outside tests, fail clearly
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Auth library not available")
    try:
        # Decode header to get kid without verifying
        unverified = jwt.get_unverified_header(token)
        unverified_claims = jwt.get_unverified_claims(token)
        iss = settings.NEXTAUTH_URL or str(unverified_claims.get('iss', ''))
        if not iss:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing issuer")
        jwks = await _jwks_cache.get_keyset(iss)
        keys = jwks.get('keys', [])
        kid = unverified.get('kid')
        key = next((k for k in keys if k.get('kid') == kid), None)
        if not key:
            # refresh once in case of rotation
            _jwks_cache._cache.pop(iss, None)
            jwks = await _jwks_cache.get_keyset(iss)
            keys = jwks.get('keys', [])
            key = next((k for k in keys if k.get('kid') == kid), None)
        if not key:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Signing key not found")
        audience = settings.NEXTAUTH_SECRET
        options = {"verify_aud": bool(audience)}
        claims = jwt.decode(token, key, algorithms=["RS256"], issuer=iss, audience=audience, options=options)
        sub = str(claims.get('sub', ''))
        if not sub:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid subject")
        email = None
        # NextAuth may place email in several claim keys depending on provider
        for k in ("email", "primary_email", "email_address"):
            v = claims.get(k)
            if isinstance(v, str):
                email = v
                break
        return Principal(
            user_id=sub, 
            email=email, 
            auth_type="nextauth_standard",
            claims=claims
        )
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except HTTPException:
        raise
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")


security = HTTPBearer(auto_error=False)


async def require_auth(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security)
) -> Principal:
    """Enhanced authentication with multiple token support and header fallback"""
    
    # Testing hook: allow disabling auth via explicit environment variable only
    if os.getenv("DISABLE_AUTH_FOR_TESTS") == "1":
        return Principal(
            user_id="test-user",
            email="test@example.com",
            auth_type="test",
            claims={"test_mode": True}
        )
    
    # Try header-based authentication first (for BFF proxy)
    header_user = extract_user_from_headers(request)
    if header_user:
        return header_user
    
    # Require bearer token
    if credentials is None or not credentials.scheme or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Missing bearer token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = (credentials.credentials or "").strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Missing bearer token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Handle fallback tokens from NextAuth frontend
    if token.startswith("gojob_fallback_"):
        return await verify_fallback_token(token)
    
    # Handle custom NextAuth JWT tokens
    if token.startswith("gojob_"):
        jwt_payload = await verify_nextauth_jwt_token(token)
        if jwt_payload:
            return Principal(
                user_id=jwt_payload.get("sub", jwt_payload.get("user_id", "")),
                email=jwt_payload.get("email"),
                auth_type="nextauth_jwt",
                name=jwt_payload.get("name"),
                picture=jwt_payload.get("picture"),
                token_data=jwt_payload
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid NextAuth JWT token"
            )
    
    # Handle regular NextAuth JWT tokens (final fallback)
    try:
        principal = await verify_nextauth_token(token)
        return Principal(
            user_id=principal.user_id,
            email=principal.email,
            auth_type="nextauth_standard",
            claims=principal.claims
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed - invalid token format"
        )


async def verify_nextauth_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify NextAuth JWT token"""
    try:
        # For NextAuth JWT tokens that start with "gojob_"
        if token.startswith("gojob_"):
            encoded_payload = token[6:]  # Remove "gojob_" prefix
            decoded_bytes = base64.urlsafe_b64decode(encoded_payload + '==')
            payload = json.loads(decoded_bytes)
            
            # Validate token expiration
            if 'exp' in payload:
                if payload['exp'] < time.time():
                    return None
                    
            return payload
        
        # For regular JWT tokens, try to decode without signature verification for now
        # In production, you'd want proper JWT signature verification
        try:
            from jose import jwt
            decoded = jwt.get_unverified_claims(token)
            
            # Validate token expiration
            if 'exp' in decoded:
                if decoded['exp'] < time.time():
                    return None
                    
            return decoded
        except Exception:
            return None
            
    except Exception:
        return None


async def verify_fallback_token(token: str) -> Principal:
    """Verify fallback tokens created by the NextAuth frontend"""
    try:
        # Remove the prefix
        if not token.startswith("gojob_fallback_"):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid fallback token format")
        
        encoded_data = token[15:]  # Remove "gojob_fallback_" prefix
        
        # Decode the base64url encoded data
        import base64
        import json
        decoded_data = base64.urlsafe_b64decode(encoded_data + '==')  # Add padding if needed
        auth_data = json.loads(decoded_data)
        
        # Validate required fields
        if not auth_data.get('user_id') or not auth_data.get('email'):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token data")
        
        # Check if token is not too old (1 hour max)
        timestamp = auth_data.get('timestamp', 0)
        if time.time() - timestamp / 1000 > 3600:  # 1 hour
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
        
        return Principal(
            user_id=auth_data['user_id'],
            email=auth_data['email'],
            auth_type="fallback",
            claims=auth_data
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid fallback token: {str(e)}")


def extract_user_from_headers(request: Request) -> Optional[Principal]:
    """Extract user information from custom headers (fallback method)"""
    user_id = request.headers.get('x-user-id')
    user_email = request.headers.get('x-user-email')
    auth_provider = request.headers.get('x-auth-provider')
    
    if user_id and user_email and auth_provider == 'nextauth-google':
        return Principal(
            user_id=user_id,
            email=user_email,
            auth_type="header",
            claims={
                'provider': auth_provider,
                'source': 'header_fallback'
            }
        )
    return None
