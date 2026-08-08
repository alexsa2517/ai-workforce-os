"""
Request/Response Logging Middleware
Logs all requests with timing, status, and body size.
"""
import logging
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("ai_workforce.middleware.logging")


class LoggingMiddleware(BaseHTTPMiddleware):
    """Log all incoming requests and responses."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Log request
        logger.info(
            f"→ Request: {request.method} {request.url.path} "
            f"| Client: {request.client.host if request.client else 'unknown'} "
            f"| UA: {request.headers.get('user-agent', 'unknown')[:50]}"
        )

        response = await call_next(request)

        duration = time.time() - start_time

        # Log response
        logger.info(
            f"← Response: {request.method} {request.url.path} "
            f"| Status: {response.status_code} "
            f"| Duration: {duration:.3f}s"
        )

        response.headers["X-Process-Time"] = f"{duration:.3f}"
        return response
