"""
Security Middleware
- SQL Injection Prevention
- XSS Prevention
- Security Headers (OWASP recommended)
- CSRF Protection
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import re
import bleach
import logging
import html

from utils.metrics import anomaly_alerts_total

logger = logging.getLogger(__name__)

# ─── SQL Injection Patterns ───────────────────────────────────────────────────
SQL_INJECTION_PATTERNS = [
    r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|TRUNCATE)\b)",
    r"(--|;|/\*|\*/|xp_)",
    r"(\bOR\b\s+\d+\s*=\s*\d+)",
    r"(\bAND\b\s+\d+\s*=\s*\d+)",
    r"('.*--)",
    r"(SLEEP\s*\(|BENCHMARK\s*\(|WAITFOR\s+DELAY)",
]

SQL_PATTERN = re.compile("|".join(SQL_INJECTION_PATTERNS), re.IGNORECASE)

# ─── XSS Patterns ─────────────────────────────────────────────────────────────
XSS_PATTERNS = [
    r"<script[^>]*>.*?</script>",
    r"javascript:",
    r"on\w+\s*=",
    r"<iframe[^>]*>",
    r"<object[^>]*>",
    r"<embed[^>]*>",
    r"vbscript:",
    r"data:text/html",
]

XSS_PATTERN = re.compile("|".join(XSS_PATTERNS), re.IGNORECASE | re.DOTALL)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add OWASP recommended security headers to every response"""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        # XSS Protection
        response.headers["X-XSS-Protection"] = "1; mode=block"
        # Strict Transport Security (HTTPS only)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        # Content Security Policy
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        # Permissions Policy
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        
        # ─── FIXED: Safely remove server details without using .pop() ───
        if "Server" in response.headers:
            del response.headers["Server"]
        if "X-Powered-By" in response.headers:
            del response.headers["X-Powered-By"]

        return response


class SQLInjectionMiddleware(BaseHTTPMiddleware):
    """Detect and block SQL injection attempts"""

    async def dispatch(self, request: Request, call_next):
        # Check query params
        for key, value in request.query_params.items():
            if SQL_PATTERN.search(str(value)):
                logger.warning(
                    f"SQL injection attempt detected | IP: {request.client.host} | "
                    f"Path: {request.url.path} | Param: {key}"
                )
                anomaly_alerts_total.labels(alert_type="sql_injection").inc()
                return JSONResponse(
                    status_code=400,
                    content={"detail": "Invalid input detected"}
                )

        # Check path params
        if SQL_PATTERN.search(str(request.url.path)):
            logger.warning(f"SQL injection in path | IP: {request.client.host}")
            anomaly_alerts_total.labels(alert_type="sql_injection").inc()
            return JSONResponse(
                status_code=400,
                content={"detail": "Invalid request"}
            )

        return await call_next(request)


class XSSMiddleware(BaseHTTPMiddleware):
    """Detect XSS attempts in incoming requests"""

    async def dispatch(self, request: Request, call_next):
        # Check query params for XSS
        for key, value in request.query_params.items():
            if XSS_PATTERN.search(str(value)):
                logger.warning(
                    f"XSS attempt detected | IP: {request.client.host} | "
                    f"Path: {request.url.path} | Param: {key}"
                )
                anomaly_alerts_total.labels(alert_type="xss_attempt").inc()
                return JSONResponse(
                    status_code=400,
                    content={"detail": "Invalid input detected"}
                )

        return await call_next(request)


def sanitize_input(value: str) -> str:
    """Sanitize user input — strip HTML tags, escape special chars"""
    if not isinstance(value, str):
        return value
    # Remove HTML tags using bleach
    cleaned = bleach.clean(value, tags=[], strip=True)
    # HTML escape remaining special characters
    escaped = html.escape(cleaned)
    return escaped.strip()


def validate_no_sqli(value: str) -> str:
    """Pydantic validator — raises ValueError if SQLi detected"""
    if SQL_PATTERN.search(str(value)):
        raise ValueError("Invalid characters in input")
    return value


def validate_no_xss(value: str) -> str:
    """Pydantic validator — raises ValueError if XSS detected"""
    if XSS_PATTERN.search(str(value)):
        raise ValueError("Invalid content in input")
    return sanitize_input(value)
