"""
MACP Research Assistant — Auth Middleware (Phase 3C)
====================================================
Unified auth context: supports both API key and JWT authentication.
get_current_user() returns User|None (guest mode compatible).
require_user() rejects unauthenticated requests.
"""

from typing import Optional

from fastapi import Cookie, Header, HTTPException, Request
from jwt import InvalidTokenError

from config import MACP_API_KEY
from database import SessionLocal, User
from github_auth import decode_jwt

import secrets


# ---------------------------------------------------------------------------
# Unified auth context
# ---------------------------------------------------------------------------


async def get_current_user(
    request: Request,
    authorization: Optional[str] = Header(default=None),
    x_api_key: Optional[str] = Header(default=None),
    macp_session: Optional[str] = Cookie(default=None),
) -> Optional[User]:
    """
    Extract user from JWT cookie, Authorization header, or API key.

    Priority:
      1. JWT in cookie (macp_session)
      2. Authorization: Bearer <JWT or API key>
      3. X-API-Key header

    Returns User object if authenticated, None for guests.
    """
    # 1. Try JWT from cookie
    if macp_session:
        user = _user_from_jwt(macp_session)
        if user:
            return user

    # 2. Try Authorization header
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
        # Try as JWT first
        user = _user_from_jwt(token)
        if user:
            return user
        # Fall back to API key
        if _verify_api_key(token):
            return None  # API key auth = authenticated but no user object

    # 3. Try X-API-Key header
    if x_api_key:
        if _verify_api_key(x_api_key):
            return None  # API key auth = authenticated but no user object
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Guest mode
    return None


async def require_user(
    request: Request,
    authorization: Optional[str] = Header(default=None),
    x_api_key: Optional[str] = Header(default=None),
    macp_session: Optional[str] = Cookie(default=None),
) -> User:
    """Require a logged-in user (not guest, not API key only)."""
    user = await get_current_user(request, authorization, x_api_key, macp_session)
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user


def is_authenticated(
    authorization: Optional[str] = None,
    x_api_key: Optional[str] = None,
    macp_session: Optional[str] = None,
) -> bool:
    """Quick check: is the request authenticated (JWT or API key)?"""
    if macp_session:
        try:
            decode_jwt(macp_session)
            return True
        except InvalidTokenError:
            pass

    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
        try:
            decode_jwt(token)
            return True
        except InvalidTokenError:
            pass
        if _verify_api_key(token):
            return True

    if x_api_key and _verify_api_key(x_api_key):
        return True

    return False


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _user_from_jwt(token: str) -> Optional[User]:
    """Decode JWT and load user from DB. Returns None on failure."""
    try:
        payload = decode_jwt(token)
    except InvalidTokenError:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == int(user_id)).first()
        if user:
            # Detach from session so it can be used outside
            db.expunge(user)
        return user
    finally:
        db.close()


def _verify_api_key(key: str) -> bool:
    """Check if a key matches the configured MACP_API_KEY."""
    if not MACP_API_KEY:
        return False
    return secrets.compare_digest(key, MACP_API_KEY)
