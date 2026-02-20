"""
MACP Research Assistant — GitHub App OAuth (Phase 3C)
=====================================================
GitHub OAuth service: authorization URL, token exchange, user upsert, JWT management.
"""

import time
from datetime import datetime, timezone
from typing import Optional

import httpx
import jwt
from cryptography.fernet import Fernet

from config import (
    GITHUB_APP_CLIENT_ID,
    GITHUB_APP_CLIENT_SECRET,
    GITHUB_APP_REDIRECT_URI,
    JWT_ALGORITHM,
    JWT_EXPIRY_HOURS,
    JWT_SECRET,
)
from database import SessionLocal, User

# ---------------------------------------------------------------------------
# Fernet encryption for GitHub access tokens at rest
# ---------------------------------------------------------------------------

# Derive a Fernet key from JWT_SECRET (must be 32 url-safe base64 bytes)
import base64
import hashlib

_fernet_key = base64.urlsafe_b64encode(hashlib.sha256(JWT_SECRET.encode()).digest())
_fernet = Fernet(_fernet_key)


def encrypt_token(plain: str) -> str:
    return _fernet.encrypt(plain.encode()).decode()


def decrypt_token(cipher: str) -> str:
    return _fernet.decrypt(cipher.encode()).decode()


# ---------------------------------------------------------------------------
# GitHub OAuth flow
# ---------------------------------------------------------------------------

GITHUB_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USER_URL = "https://api.github.com/user"


def get_authorize_url(state: Optional[str] = None) -> str:
    """Build the GitHub OAuth authorization URL."""
    params = {
        "client_id": GITHUB_APP_CLIENT_ID,
        "redirect_uri": GITHUB_APP_REDIRECT_URI,
        "scope": "read:user repo",
    }
    if state:
        params["state"] = state
    qs = "&".join(f"{k}={v}" for k, v in params.items())
    return f"{GITHUB_AUTHORIZE_URL}?{qs}"


async def exchange_code_for_token(code: str) -> str:
    """Exchange an OAuth code for a GitHub access token."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            GITHUB_TOKEN_URL,
            json={
                "client_id": GITHUB_APP_CLIENT_ID,
                "client_secret": GITHUB_APP_CLIENT_SECRET,
                "code": code,
                "redirect_uri": GITHUB_APP_REDIRECT_URI,
            },
            headers={"Accept": "application/json"},
        )
        resp.raise_for_status()
        data = resp.json()
    token = data.get("access_token")
    if not token:
        raise ValueError(f"GitHub OAuth error: {data.get('error_description', 'no access_token')}")
    return token


async def get_github_user(access_token: str) -> dict:
    """Fetch the authenticated GitHub user profile."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            GITHUB_USER_URL,
            headers={"Authorization": f"Bearer {access_token}", "Accept": "application/json"},
        )
        resp.raise_for_status()
        return resp.json()


# ---------------------------------------------------------------------------
# User management
# ---------------------------------------------------------------------------


def upsert_user(github_user: dict, access_token: str) -> User:
    """Create or update a user from GitHub profile data."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.github_id == github_user["id"]).first()
        if user:
            user.github_login = github_user.get("login", user.github_login)
            user.github_name = github_user.get("name", "") or ""
            user.github_avatar_url = github_user.get("avatar_url", "") or ""
            user.github_access_token = encrypt_token(access_token)
            user.last_login = datetime.now(timezone.utc)
        else:
            user = User(
                github_id=github_user["id"],
                github_login=github_user.get("login", ""),
                github_name=github_user.get("name", "") or "",
                github_avatar_url=github_user.get("avatar_url", "") or "",
                github_access_token=encrypt_token(access_token),
            )
            db.add(user)
        db.commit()
        db.refresh(user)
        return user
    finally:
        db.close()


# ---------------------------------------------------------------------------
# JWT
# ---------------------------------------------------------------------------


def create_jwt(user: User) -> str:
    """Create a JWT for the given user."""
    payload = {
        "sub": str(user.id),
        "github_id": user.github_id,
        "github_login": user.github_login,
        "iat": int(time.time()),
        "exp": int(time.time()) + JWT_EXPIRY_HOURS * 3600,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_jwt(token: str) -> dict:
    """Decode and validate a JWT. Raises jwt.InvalidTokenError on failure."""
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
