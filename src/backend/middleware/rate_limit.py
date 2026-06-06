"""
Rate Limiting Middleware
Using slowapi (Starlette-compatible rate limiting)
Prevents brute force attacks
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["60/minute"],
    headers_enabled=True,
)


async def rate_limit_handler(request: Request, exc):
    """Custom handler — don't expose internal rate limit details"""
    logger.warning(f"Rate limit exceeded | IP: {request.client.host} | Path: {request.url.path}")
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Please try again later."},
        headers={"Retry-After": "60"},
    )
