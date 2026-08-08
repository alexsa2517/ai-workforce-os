"""
Rate Limiting Configuration
Uses slowapi for in-memory rate limiting.
In production, use Redis-backed limiter.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.config import settings

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.RATE_LIMIT],
)


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Custom handler for rate limit exceeded."""
    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "error_code": "rate_limit_exceeded",
            "detail": f"Too many requests. Limit: {settings.RATE_LIMIT}",
            "retry_after": exc.detail.get("retry_after", 60) if hasattr(exc, "detail") else 60,
        },
    )
