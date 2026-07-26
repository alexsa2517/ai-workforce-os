"""
Logging Middleware - Logs all incoming requests and outgoing responses
"""

import time
import logging

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("ai_workforce.middleware")


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware that logs all HTTP requests and responses."""

    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()

        # Log request
        logger.info(
            f"REQUEST | {request.method} {request.url.path} | "
            f"Client: {request.client.host if request.client else 'unknown'}"
        )

        # Process request
        response = await call_next(request)

        # Log response
        duration = time.time() - start_time
        logger.info(
            f"RESPONSE | {request.method} {request.url.path} | "
            f"Status: {response.status_code} | "
            f"Duration: {duration:.4f}s"
        )

        return response
