"""Security middleware: HTTP security headers added to every response."""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, RedirectResponse

from backend.config import get_settings

_settings = get_settings()


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add OWASP-recommended security headers to every HTTP response."""

    async def dispatch(self, request: Request, call_next) -> Response:
        # Redirect HTTP → HTTPS in production (when behind a reverse proxy)
        if not _settings.debug and request.headers.get("x-forwarded-proto") == "http":
            https_url = str(request.url).replace("http://", "https://", 1)
            return RedirectResponse(url=https_url, status_code=301)

        response = await call_next(request)
        # Prevent MIME-type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        # Block the response from being loaded in an iframe (clickjacking)
        response.headers["X-Frame-Options"] = "DENY"
        # Disable legacy XSS filter (modern browsers; CSP is the real defence)
        response.headers["X-XSS-Protection"] = "0"
        # Enforce HTTPS for 1 year, include subdomains
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        # Restrict what the browser is allowed to load.
        # AI calls are now proxied through the backend — no external API domains needed.
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: blob:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        # Don't send the Referer header to external sites
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        # Limit browser feature access
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=()"
        )
        # Remove server fingerprinting header if present
        if "server" in response.headers:
            del response.headers["server"]
        # Prevent browsers from caching API responses
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"
        return response
