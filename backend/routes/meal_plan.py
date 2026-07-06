"""Meal plan route — personalised daily plan generation via IBM Granite."""

import structlog
from fastapi import APIRouter, Depends, HTTPException, status

from backend.api.dependencies import get_current_user
from backend.models.auth import UserPublic
from backend.models.meal_plan import MealPlanRequest, MealPlanResponse
from backend.services.meal_plan_service import generate_meal_plan

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.post(
    "/",
    response_model=MealPlanResponse,
    summary="Generate a personalised daily meal plan",
    status_code=status.HTTP_201_CREATED,
)
async def create_meal_plan(
    payload: MealPlanRequest,
    current_user: UserPublic = Depends(get_current_user),
) -> MealPlanResponse:
    """
    Generate a complete one-day meal plan personalised to the user's profile.

    **Input fields:**
    - `age`, `height_cm`, `weight_kg`, `gender` — biometrics
    - `goal` — weight_loss | weight_gain | maintenance | muscle_gain
    - `diseases` — list of medical conditions (e.g. ["diabetes", "hypertension"])
    - `allergies` — list of allergens (e.g. ["nuts", "gluten"])
    - `cuisine_preference` — list of preferred cuisines (e.g. ["Indian", "Mediterranean"])
    - `budget_usd_per_day` — optional daily food budget in USD
    - `lifestyle` — activity level from sedentary to extra_active

    **Response includes:**
    - Breakfast, lunch, dinner, and snacks — each with ingredients, macros, instructions
    - Full daily nutrition summary (calories, protein, carbs, fat, fibre, water)
    - An overall `explanation` for why this plan suits the user
    """
    if payload.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="user_id in body must match the authenticated user.",
        )

    try:
        plan = generate_meal_plan(payload)
    except ValueError as exc:
        logger.error("Meal plan JSON parse failure", user_id=current_user.id, error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The AI returned an unreadable response. Please try again.",
        ) from exc
    except RuntimeError as exc:
        logger.error("Meal plan inference failure", user_id=current_user.id, error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The AI service is temporarily unavailable. Please try again.",
        ) from exc

    logger.info("Meal plan delivered", user_id=current_user.id)
    return plan
