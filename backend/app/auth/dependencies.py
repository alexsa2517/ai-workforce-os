"""
Auth Dependencies - FastAPI dependency functions for authentication

Provides get_current_user and optional authentication dependencies.
"""

import logging
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.jwt_utils import decode_access_token, TokenPayload

logger = logging.getLogger("ai_workforce.auth.dependencies")

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[TokenPayload]:
    """
    Get the current authenticated user from JWT token.

    Args:
        credentials: HTTP Bearer token credentials

    Returns:
        TokenPayload if authenticated, None if no token provided

    Raises:
        HTTPException: If token is invalid
    """
    if credentials is None:
        return None

    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


async def require_auth(
    user: Optional[TokenPayload] = Depends(get_current_user),
) -> TokenPayload:
    """
    Require authentication - raises 401 if no valid token.

    Args:
        user: Current user from get_current_user dependency

    Returns:
        TokenPayload of the authenticated user

    Raises:
        HTTPException: If user is not authenticated
    """
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
