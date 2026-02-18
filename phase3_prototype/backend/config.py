"""
MACP Research Assistant — Configuration (P3B-03)
=================================================
Loads all configuration from environment variables / .env file.
Single source of truth for all settings across backend, MCP server, and CLI.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from the backend directory
_backend_dir = Path(__file__).resolve().parent
load_dotenv(_backend_dir / ".env")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

TOOLS_DIR = str((_backend_dir / ".." / ".." / "tools").resolve())
MACP_DIR = str((_backend_dir / ".." / ".." / ".macp").resolve())

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

_default_db = f"sqlite:///{MACP_DIR}/macp.db"
DATABASE_URL: str = os.getenv("MACP_DATABASE_URL", _default_db)

# ---------------------------------------------------------------------------
# Rate Limits
# ---------------------------------------------------------------------------

RATE_LIMIT_SEARCH: str = os.getenv("RATE_LIMIT_SEARCH", "30/minute")
RATE_LIMIT_ANALYZE: str = os.getenv("RATE_LIMIT_ANALYZE", "10/minute")
RATE_LIMIT_GUEST_SEARCH: str = os.getenv("RATE_LIMIT_GUEST_SEARCH", "5/day")
RATE_LIMIT_GUEST_ANALYZE: str = os.getenv("RATE_LIMIT_GUEST_ANALYZE", "2/day")

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------

CORS_ORIGINS: list[str] = [
    o.strip()
    for o in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
    if o.strip()
]

# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

MACP_API_KEY: str | None = os.getenv("MACP_API_KEY")

# ---------------------------------------------------------------------------
# HTTPS
# ---------------------------------------------------------------------------

ENFORCE_HTTPS: bool = os.getenv("ENFORCE_HTTPS", "false").lower() in ("true", "1", "yes")

# ---------------------------------------------------------------------------
# MCP Server
# ---------------------------------------------------------------------------

MCP_SERVER_PORT: int = int(os.getenv("MCP_SERVER_PORT", "8001"))
