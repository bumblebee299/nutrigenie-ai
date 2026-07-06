"""Healthy Food Swap route."""

import structlog
from fastapi import APIRouter, Depends, HTTPException, status

from backend.api.dependencies import get_current_user
from backend.models.auth import UserPublic
from backend.models.food_swap import FoodSwapRequest, FoodSwapResponse
from backend.services.food_swap_service import suggest_food_swaps

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.post(
    "/",
    response_model=FoodSwapResponse,
    summary="Get healthier food swap suggestions",
    status_code=status.HTTP_200_OK,
)
async def get_food_swaps(
    payload: FoodSwapRequest,
    current_user: UserPublic = Depends(get_current_user),
) -> FoodSwapResponse:
    """
    Suggest 3 healthier alternatives for any food item.

    Each swap includes:
    - The healthier option name
    - Estimated calorie reduction per serving
    - List of nutritional benefits
    - A practical preparation tip
    - A brief explanation of the science behind the swap
    """
    if payload.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="user_id in body must match the authenticated user.",
        )

    try:
        result = suggest_food_swaps(payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The AI returned an unreadable response. Please try again.",
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The AI service is temporarily unavailable. Please try again.",
        ) from exc

    logger.info("Food swaps delivered", user_id=current_user.id, food=payload.food_item)
    return result
