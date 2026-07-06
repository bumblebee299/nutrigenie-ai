"""Authentication routes — register, login, token refresh, logout."""

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from backend.api.dependencies import get_current_user
from backend.models.auth import (
    TokenRefreshRequest,
    TokenResponse,
    UserPublic,
    UserRegister,
)
from backend.services.auth_service import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)
from backend.services.user_service import authenticate_user, create_user, get_user_by_id

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.post(
    "/register",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
async def register(payload: UserRegister) -> UserPublic:
    """
    Create a new user account.

    - Validates that the email is not already registered.
    - Hashes the password with bcrypt before persisting.
    - Returns the public user representation (no password).
    """
    try:
        user = create_user(
            name=payload.name,
            email=payload.email,
            password=payload.password,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    logger.info("New user registered", user_id=user.id, email=user.email)
    return user


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate and receive JWT tokens",
)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> TokenResponse:
    """
    Authenticate with email + password (OAuth2 password flow).

    Returns a short-lived access token and a long-lived refresh token.
    """
    doc = authenticate_user(email=form_data.username, password=form_data.password)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: str = doc["_id"]
    logger.info("User logged in", user_id=user_id)

    return TokenResponse(
        access_token=create_access_token(user_id),
        refresh_token=create_refresh_token(user_id),
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Exchange a refresh token for a new access token",
)
async def refresh_token(payload: TokenRefreshRequest) -> TokenResponse:
    """
    Issue a new access token using a valid refresh token.

    The refresh token itself is **not** rotated to keep the flow simple;
    rotation can be added as a security hardening step in production.
    """
    try:
        user_id = decode_refresh_token(payload.refresh_token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    doc = get_user_by_id(user_id)
    if not doc or not doc.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found or inactive.",
        )

    return TokenResponse(
        access_token=create_access_token(user_id),
        refresh_token=create_refresh_token(user_id),
    )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Invalidate the current session",
)
async def logout(current_user: UserPublic = Depends(get_current_user)) -> None:
    """
    Logout the currently authenticated user.

    Because JWTs are stateless, true server-side invalidation requires a
    deny-list (e.g., Redis). This endpoint signals logout to clients and
    is the hook point for implementing a deny-list in a hardening pass.
    """
    logger.info("User logged out", user_id=current_user.id)


@router.get(
    "/me",
    response_model=UserPublic,
    summary="Get the currently authenticated user",
)
async def me(current_user: UserPublic = Depends(get_current_user)) -> UserPublic:
    """Return the public profile of the authenticated user."""
    return current_user
