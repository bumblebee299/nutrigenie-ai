"""Profile routes — retrieve and update the authenticated user's profile."""

import structlog
from fastapi import APIRouter, Depends, HTTPException, Path, status

from backend.api.dependencies import get_current_user
from backend.models.auth import UserPublic
from backend.models.profile import ProfileResponse, ProfileUpdate
from backend.services.user_service import get_profile, update_profile

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.get(
    "/{user_id}",
    response_model=ProfileResponse,
    summary="Get a user's full profile",
)
async def get_user_profile(
    user_id: str = Path(..., description="The UUID of the user"),
    current_user: UserPublic = Depends(get_current_user),
) -> ProfileResponse:
    """
    Return the full profile for a user.

    Users can only access their own profile unless an admin role is added
    in a future task.
    """
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this profile.",
        )

    try:
        return get_profile(user_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch(
    "/{user_id}",
    response_model=ProfileResponse,
    summary="Partially update a user's profile",
)
async def patch_user_profile(
    payload: ProfileUpdate,
    user_id: str = Path(..., description="The UUID of the user"),
    current_user: UserPublic = Depends(get_current_user),
) -> ProfileResponse:
    """
    Apply a partial update (PATCH semantics) to the user's profile.

    Only fields explicitly provided in the request body are updated;
    omitted fields retain their existing values.
    """
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this profile.",
        )

    try:
        updated = update_profile(user_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    logger.info("Profile updated via API", user_id=user_id)
    return updated
