"""
MACP Research Assistant — Guest Mode (P3B-05)
===============================================
IP-based rate limiting for unauthenticated users.
Uses an in-memory cache with daily expiry.
"""

from collections import defaultdict
from datetime import date
from typing import NamedTuple

from fastapi import HTTPException, Request

from config import RATE_LIMIT_GUEST_SEARCH, RATE_LIMIT_GUEST_ANALYZE


def _parse_limit(limit_str: str) -> int:
    """Parse '5/day' or '2/day' to just the integer count."""
    return int(limit_str.split("/")[0])


GUEST_SEARCH_LIMIT = _parse_limit(RATE_LIMIT_GUEST_SEARCH)
GUEST_ANALYZE_LIMIT = _parse_limit(RATE_LIMIT_GUEST_ANALYZE)


class DayCounter(NamedTuple):
    day: date
    count: int


# In-memory counters: ip -> {action -> DayCounter}
_counters: dict[str, dict[str, DayCounter]] = defaultdict(dict)


def _get_ip(request: Request) -> str:
    """Get the client IP, respecting X-Forwarded-For."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def check_guest_limit(request: Request, action: str) -> None:
    """
    Check and increment the guest rate limit for an action.

    Args:
        request: The FastAPI request.
        action: 'search' or 'analyze'.

    Raises:
        HTTPException 429 if the guest limit is exceeded.
    """
    ip = _get_ip(request)
    today = date.today()

    limit = GUEST_SEARCH_LIMIT if action == "search" else GUEST_ANALYZE_LIMIT

    current = _counters[ip].get(action)

    # Reset if it's a new day
    if current is None or current.day != today:
        _counters[ip][action] = DayCounter(day=today, count=1)
        return

    if current.count >= limit:
        raise HTTPException(
            status_code=429,
            detail=f"Guest limit exceeded: {limit} {action}(es) per day. "
            f"Provide an API key for unlimited access.",
        )

    _counters[ip][action] = DayCounter(day=today, count=current.count + 1)
