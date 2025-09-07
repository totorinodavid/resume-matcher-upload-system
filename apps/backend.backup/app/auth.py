"""
Compatibility shim exposing NextAuth JWT verification for imports as `app.auth`.
"""
from .core.auth import Principal, verify_nextauth_token, require_auth  # re-export
