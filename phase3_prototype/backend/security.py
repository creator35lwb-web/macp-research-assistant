"""
MACP Research Assistant — Security Headers Middleware (Phase 3C)
================================================================
Equivalent to Helmet.js for Python/FastAPI.
Adds CSP, HSTS, X-Frame-Options, and other security headers to every response.
"""

import hmac
import os

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from config import ENFORCE_HTTPS


class OriginGuardMiddleware(BaseHTTPMiddleware):
    """Block direct origin access to /api/* when fronted by Cloudflare.

    Opt-in and a no-op until ``CF_ORIGIN_SECRET`` is set. When set, Cloudflare
    injects a matching ``X-Origin-Secret`` header (via an Origin/Transform rule),
    and any /api/* request lacking it — i.e. a direct ``*.run.app`` hit that
    bypasses Cloudflare's WAF/rate-limiting — is rejected with 403.

    Scoped to /api/* only, so static assets, the SPA, and health checks stay
    reachable directly (Cloud Run's own probes won't be blocked). Comparison is
    constant-time. Until you configure Cloudflare + the env var, behaviour is
    unchanged — safe to deploy now.
    """

    async def dispatch(self, request: Request, call_next):
        secret = os.environ.get("CF_ORIGIN_SECRET", "")
        if secret and request.url.path.startswith("/api/"):
            provided = request.headers.get("x-origin-secret", "")
            if not hmac.compare_digest(provided, secret):
                return JSONResponse(status_code=403, content={"detail": "Forbidden"})
        return await call_next(request)


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
