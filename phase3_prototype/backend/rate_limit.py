"""
Shared rate limiter (slowapi).

Extracted from main.py so both the main app and the WebMCP router (webmcp.py)
can apply `@limiter.limit(...)` without a circular import (main.py imports the
mcp_router from webmcp, so webmcp cannot import the limiter from main).

Import graph (no cycles): middleware -> (database, github_auth);
rate_limit -> middleware; webmcp -> {middleware, rate_limit};
main -> {webmcp, rate_limit}.
"""

from fastapi import Request
from slowapi import Limiter

from middleware import is_authenticated


def _get_real_client_ip(request: Request) -> str:
    """Extract the true client IP from X-Forwarded-For.

    Cloud Run appends the real client IP as the LAST entry in the chain.
    Reading the first entry is exploitable — attackers can prepend fake IPs
    to bypass per-IP rate limits. Always use the last entry on Cloud Run.
    """
    forwarded_for = request.headers.get("X-Forwarded-For", "")
    if forwarded_for:
        ips = [ip.strip() for ip in forwarded_for.split(",")]
        return ips[-1]  # Last IP = Cloud Run's addition = real client
    return request.client.host or "unknown"


def _rate_limit_key(request: Request) -> str:
    """3-tier rate limit key.

    - Authenticated (JWT): user:{user_id}
    - Authenticated (API key): apikey:{ip}
    - Guest: guest:{ip}
    """
    auth = request.headers.get("authorization")
    api_key = request.headers.get("x-api-key")
    cookie = request.cookies.get("macp_session")

    if is_authenticated(authorization=auth, x_api_key=api_key, macp_session=cookie):
        from github_auth import decode_jwt
        from jwt import InvalidTokenError
        for token in [cookie, auth[7:] if auth and auth.startswith("Bearer ") else None]:
            if token:
                try:
                    payload = decode_jwt(token)
                    return f"user:{payload.get('sub', 'unknown')}"
                except InvalidTokenError:
                    pass
        return f"apikey:{_get_real_client_ip(request)}"

    return f"guest:{_get_real_client_ip(request)}"


limiter = Limiter(key_func=_rate_limit_key)
