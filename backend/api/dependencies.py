"""FastAPI dependency injection helpers — current-user extraction from JWT."""

import structlog
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from backend.models.auth import UserPublic
from backend.services.auth_service import decode_access_token
from backend.services.user_service import get_user_by_id

logger = structlog.get_logger(__name__)

_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(_oauth2_scheme)) -> UserPublic:
    """
    FastAPI dependency that extracts and validates the Bearer token,
    then loads and returns the authenticated user.

    Raises:
        HTTPException 401: if the token is missing, invalid, or expired.
        HTTPException 401: if the user no longer exists or is inactive.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        user_id = decode_access_token(token)
    except ValueError as exc:
        logger.warning("Token validation failed", error=str(exc))
        raise credentials_exception from exc

    doc = get_user_by_id(user_id)
    if not doc:
        logger.warning("Authenticated user not found in database", user_id=user_id)
        raise credentials_exception

    if not doc.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="This account has been deactivated.",
        )

    from datetime import datetime

    return UserPublic(
        id=doc["_id"],
        name=doc["name"],
        email=doc["email"],
        created_at=datetime.fromisoformat(doc["created_at"]),
        is_active=doc.get("is_active", True),
    )
