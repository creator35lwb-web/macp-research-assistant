"""
MACP Research Assistant — Security Headers Middleware (Phase 3C)
================================================================
Equivalent to Helmet.js for Python/FastAPI.
Adds CSP, HSTS, X-Frame-Options, and other security headers to every response.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from config import ENFORCE_HTTPS


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)

        # Prevent MIME sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Prevent framing (clickjacking protection)
        response.headers["X-Frame-Options"] = "DENY"

        # Modern browsers: CSP is preferred over X-XSS-Protection
        response.headers["X-XSS-Protection"] = "0"

        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions policy (disable unused APIs)
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"

        # Content Security Policy
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "font-src 'self' https://cdn.jsdelivr.net; "
            "frame-src https://arxiv.org; "
            "img-src 'self' https://avatars.githubusercontent.com data:; "
            "connect-src 'self' https://api.github.com"
        )

        # HSTS (only when HTTPS is enforced)
        if ENFORCE_HTTPS:
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )

        return response
