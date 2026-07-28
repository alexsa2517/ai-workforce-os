"""
JWT Utilities - Token generation, validation, and decoding
Provides JWT-based authentication for the AI Workforce OS API.
"""
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from pydantic import BaseModel, Field
from app.core.config import settings

logger = logging.getLogger("ai_workforce.auth")

# JWT configuration from settings
JWT_SECRET = settings.JWT_SECRET or os.getenv("JWT_SECRET", "ai-workforce-os-dev-secret-change-in-production")
JWT_ALGORITHM = settings.JWT_ALGORITHM
JWT_EXPIRATION_HOURS = settings.JWT_EXPIRATION_HOURS


class TokenPayload(BaseModel):
    """JWT token payload schema."""
    sub: str = Field(..., description="Subject (user ID)")
    role: str = Field(default="user", description="User role")
    exp: Optional[int] = None
    iat: Optional[int] = None


class TokenResponse(BaseModel):
    """Token response schema."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a JWT access token.

    Args:
        data: Payload data (must include 'sub')
        expires_delta: Token expiration duration

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(hours=JWT_EXPIRATION_HOURS)
    )
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    })
    encoded = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    logger.info(f"Token created for user: {data.get('sub')}")
    return encoded


def decode_access_token(token: str) -> Optional[TokenPayload]:
    """
    Decode and validate a JWT access token.

    Args:
        token: JWT token string

    Returns:
        TokenPayload if valid, None if invalid
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return TokenPayload(**payload)
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {e}")
        return None
