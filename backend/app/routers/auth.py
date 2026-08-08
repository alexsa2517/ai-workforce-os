"""
Auth Router - JWT token generation and validation
"""
import logging
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.schemas import TokenRequest, TokenResponse
from app.core.config import settings
from app.middleware.error_handler import APIError
import jwt

logger = logging.getLogger("ai_workforce.routers.auth")

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])
security = HTTPBearer(auto_error=False)

# Simple user store (in production, use database with hashed passwords)
# Format: {username: {password_hash, role}}
_USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "user": {"password": "user123", "role": "user"},
}


@router.post("/login", response_model=TokenResponse)
async def login(credentials: TokenRequest):
    """Authenticate and get JWT token."""
    user = _USERS.get(credentials.username)

    if not user or user["password"] != credentials.password:
        raise APIError(
            message="Invalid username or password",
            status_code=401,
            error_code="invalid_credentials",
        )

    expire = datetime.now(timezone.utc) + timedelta(hours=settings.JWT_EXPIRATION_HOURS)

    payload = {
        "sub": credentials.username,
        "role": user["role"],
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }

    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    logger.info(f"Token created for user: {credentials.username}")

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.JWT_EXPIRATION_HOURS * 3600,
    )


@router.get("/me")
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user info."""
    if not credentials:
        raise HTTPException(status_code=401, detail="No token provided")

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return {
            "username": payload["sub"],
            "role": payload.get("role", "user"),
            "exp": payload["exp"],
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
