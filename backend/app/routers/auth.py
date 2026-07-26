"""
Auth Router - Authentication endpoints for login and token management
"""

import logging
from datetime import timedelta

from fastapi import APIRouter, HTTPException

from app.auth.jwt_utils import create_access_token, TokenResponse
from app.core.config import settings

logger = logging.getLogger("ai_workforce.routers.auth")

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


class LoginRequest:
    """Login request model (simplified for initial implementation)."""
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password


@router.post("/login", response_model=TokenResponse)
async def login(request: dict):
    """
    Authenticate user and return JWT token.

    In production, this should validate against a database.
    Currently uses a simple check for demonstration.
    """
    username = request.get("username", "")
    password = request.get("password", "")

    # Simple validation (replace with database lookup in production)
    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password are required")

    # Demo credentials (replace with proper auth in production)
    if username == "admin" and password == "admin123":
        token = create_access_token(
            data={"sub": username, "role": "admin"},
            expires_delta=timedelta(hours=24),
        )
        logger.info(f"User '{username}' logged in successfully")
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            expires_in=86400,
        )

    # Accept any non-empty credentials for development
    if len(password) >= 6:
        token = create_access_token(
            data={"sub": username, "role": "user"},
            expires_delta=timedelta(hours=24),
        )
        logger.info(f"User '{username}' logged in (dev mode)")
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            expires_in=86400,
        )

    raise HTTPException(status_code=401, detail="Invalid credentials")


@router.post("/refresh")
async def refresh_token():
    """Refresh an expired token (placeholder)."""
    return {"message": "Token refresh endpoint - implement with refresh token logic"}
