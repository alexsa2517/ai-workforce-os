from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import os

class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        exempt_paths = ["/", "/docs", "/redoc", "/openapi.json", "/health"]
        if request.url.path in exempt_paths:
            return await call_next(request)
        expected_key = os.getenv("APP_API_KEY")
        if not expected_key:
            return await call_next(request)
        api_key = request.headers.get("X-API-KEY")
        if api_key != expected_key:
            raise HTTPException(status_code=403, detail="Invalid or missing API Key")
        return await call_next(request)
