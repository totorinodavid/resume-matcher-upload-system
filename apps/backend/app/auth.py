"""
Compatibility shim exposing Clerk JWT verification for imports as `app.auth`.
"""
from .core.auth import Principal, verify_clerk_token, require_auth  # re-export
