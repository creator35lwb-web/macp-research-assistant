"""
MACP Research Assistant — Authentication (P3B-02)
==================================================
API key-based authentication for the FastAPI backend and MCP server.
Keys are validated against the MACP_API_KEY environment variable.

Guest mode: unauthenticated users get limited access (P3B-05).
"""

import hashlib
import secrets
from typing import Optional

from fastapi import Header, HTTPException, Request

from config import MACP_API_KEY

# ---------------------------------------------------------------------------
# Key generation (utility)
# ---------------------------------------------------------------------------


def generate_api_key() -> tuple[str, str]:
    """
    Generate a new MACP API key.

    Returns:
        (plain_key, key_hash) — plain shown once, hash for comparison.
    """
    prefix = secrets.token_hex(4)
    body = secrets.token_urlsafe(32)
    plain_key = f"macp_{prefix}_{body}"
    key_hash = hashlib.sha256(plain_key.encode()).hexdigest()
    return plain_key, key_hash


# ---------------------------------------------------------------------------
# FastAPI dependency
# ---------------------------------------------------------------------------


def verify_api_key(key: str) -> bool:
    """Check if a key matches the configured MACP_API_KEY."""
    if not MACP_API_KEY:
        return False
    return secrets.compare_digest(key, MACP_API_KEY)


async def get_api_key(
    request: Request,
    authorization: Optional[str] = Header(default=None),
    x_api_key: Optional[str] = Header(default=None),
) -> Optional[str]:
    """
    Extract and validate the API key from request headers.

    Accepts:
      - Authorization: Bearer <key>
      - X-API-Key: <key>

    Returns the key if valid, None for guest mode.
    Raises 401 if a key is provided but invalid.
    """
    key = None

    if authorization and authorization.startswith("Bearer "):
        key = authorization[7:]
    elif x_api_key:
        key = x_api_key

    if key:
        if verify_api_key(key):
            return key
        raise HTTPException(status_code=401, detail="Invalid API key")

    # No key provided — guest mode
    return None


async def require_api_key(
    request: Request,
    authorization: Optional[str] = Header(default=None),
    x_api_key: Optional[str] = Header(default=None),
) -> str:
    """Require a valid API key — rejects guests."""
    key = None

    if authorization and authorization.startswith("Bearer "):
        key = authorization[7:]
    elif x_api_key:
        key = x_api_key

    if not key:
        raise HTTPException(status_code=401, detail="API key required")

    if not verify_api_key(key):
        raise HTTPException(status_code=401, detail="Invalid API key")

    return key
