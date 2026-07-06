"""Weekly Progress Dashboard route."""

import structlog
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from backend.api.dependencies import get_current_user
from backend.models.auth import UserPublic
from backend.models.dashboard import (
    DashboardResponse,
    LogMealRequest,
    LogWaterRequest,
    LogWeightRequest,
    LogFeedbackRequest,
)
from backend.services.dashboard_service import (
    get_weekly_dashboard,
    log_meal,
    log_water,
    log_weight,
    log_feedback,
)

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.get(
    "/{user_id}",
    response_model=DashboardResponse,
    summary="Get the weekly progress dashboard for a user",
)
async def get_dashboard(
    user_id: str = Path(..., description="User UUID"),
    week_start: date = Query(..., description="ISO-8601 date of the week's Monday (e.g. 2024-01-01)"),
    current_user: UserPublic = Depends(get_current_user),
) -> DashboardResponse:
    """
    Retrieve 7-day aggregated progress for a user.

    **Response includes:**
    - Daily entries: calories consumed, protein, water intake, weight
    - Weekly summary: averages, weight change, goal adherence %
    - Chart-ready series arrays for Recharts (calories, protein, water, weight)
    """
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own dashboard.",
        )

    try:
        dashboard = get_weekly_dashboard(user_id, week_start)
    except Exception as exc:
        logger.error("Dashboard fetch failed", user_id=user_id, error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load dashboard data.",
        ) from exc

    return dashboard


@router.post(
    "/{user_id}/meal",
    summary="Log a meal for a user on a given day",
)
async def add_user_meal(
    payload: LogMealRequest,
    user_id: str = Path(..., description="User UUID"),
    current_user: UserPublic = Depends(get_current_user),
) -> dict:
    """Log a meal and update daily calorie and protein totals."""
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only log meals for yourself.",
        )

    try:
        doc = log_meal(
            user_id=user_id,
            log_date=payload.date,
            meal_type=payload.type,
            name=payload.name,
            calories=payload.calories,
            protein_g=payload.protein_g,
        )
        return {"status": "success", "message": "Meal logged successfully", "data": doc}
    except Exception as exc:
        logger.error("Meal logging failed", user_id=user_id, error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to log meal.",
        ) from exc


@router.post(
    "/{user_id}/water",
    summary="Track water intake for a user",
)
async def add_user_water(
    payload: LogWaterRequest,
    user_id: str = Path(..., description="User UUID"),
    current_user: UserPublic = Depends(get_current_user),
) -> dict:
    """Log water intake in ml."""
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only track water for yourself.",
        )

    try:
        doc = log_water(
            user_id=user_id,
            log_date=payload.date,
            amount_ml=payload.amount_ml,
        )
        return {"status": "success", "message": "Water logged successfully", "data": doc}
    except Exception as exc:
        logger.error("Water logging failed", user_id=user_id, error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to log water intake.",
        ) from exc


@router.post(
    "/{user_id}/weight",
    summary="Log daily weight for a user",
)
async def add_user_weight(
    payload: LogWeightRequest,
    user_id: str = Path(..., description="User UUID"),
    current_user: UserPublic = Depends(get_current_user),
) -> dict:
    """Log daily weight in kg and update user profile."""
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only log weight for yourself.",
        )

    try:
        doc = log_weight(
            user_id=user_id,
            log_date=payload.date,
            weight_kg=payload.weight_kg,
        )
        return {"status": "success", "message": "Weight logged successfully", "data": doc}
    except Exception as exc:
        logger.error("Weight logging failed", user_id=user_id, error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to log weight.",
        ) from exc


@router.post(
    "/{user_id}/feedback",
    summary="Submit daily rating and feedback comments",
)
async def add_user_feedback(
    payload: LogFeedbackRequest,
    user_id: str = Path(..., description="User UUID"),
    current_user: UserPublic = Depends(get_current_user),
) -> dict:
    """Submit a 5-star rating and notes for the day."""
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only submit daily feedback for yourself.",
        )

    if payload.rating < 1 or payload.rating > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating must be between 1 and 5.",
        )

    try:
        doc = log_feedback(
            user_id=user_id,
            log_date=payload.date,
            rating=payload.rating,
            comment=payload.comment,
        )
        return {"status": "success", "message": "Daily feedback logged successfully", "data": doc}
    except Exception as exc:
        logger.error("Feedback logging failed", user_id=user_id, error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to log daily feedback.",
        ) from exc

