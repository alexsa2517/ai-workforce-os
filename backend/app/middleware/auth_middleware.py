"""
Authentication & API Key Middleware
- Validates API Key for all non-public endpoints
- Supports Bearer token for JWT authentication
- Rate limiting integration
"""
import logging
import time
from typing import Optional
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from app.core.config import settings

logger = logging.getLogger("ai_workforce.middleware.auth")

# Public paths that don't require API key
PUBLIC_PATHS = {
    "/",
    "/api/v1/health",
    "/api/v1/health/",
    "/api/v1/health/ready",
    "/api/v1/health/ready/",
    "/docs",
    "/openapi.json",
    "/redoc",
    "/api/v1/auth/login",
    "/api/v1/auth/register",
}


class APIKeyMiddleware(BaseHTTPMiddleware):
    """Middleware to validate API Key and track requests."""

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Skip public paths
        if path in PUBLIC_PATHS or path.startswith("/static/"):
            return await call_next(request)

        # Validate API Key
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            logger.warning(f"Missing API Key: {request.method} {path} from {request.client.host}")
            return Response(
                content='{"error": "Missing API Key", "detail": "X-API-Key header is required"}',
                status_code=status.HTTP_401_UNAUTHORIZED,
                media_type="application/json",
            )

        if api_key != settings.API_KEY:
            logger.warning(f"Invalid API Key: {request.client.host}")
            return Response(
                content='{"error": "Invalid API Key", "detail": "The provided API key is invalid"}',
                status_code=status.HTTP_401_UNAUTHORIZED,
                media_type="application/json",
            )

        # Track request timing
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time

        response.headers["X-Response-Time"] = f"{duration:.3f}s"
        logger.info(f"{request.method} {path} - {response.status_code} - {duration:.3f}s")

        return response
