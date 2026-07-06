"""Food Image Analysis route — upload and analyse food photos."""

import structlog
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from backend.api.dependencies import get_current_user
from backend.models.auth import UserPublic
from backend.models.image_analysis import ImageAnalysisResponse
from backend.services.image_analysis_service import analyse_food_image

logger = structlog.get_logger(__name__)
router = APIRouter()

_MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


@router.post(
    "/",
    response_model=ImageAnalysisResponse,
    summary="Analyse a food image for nutritional content",
    status_code=status.HTTP_200_OK,
)
async def analyse_image(
    user_id: str = Form(..., description="Authenticated user's UUID"),
    image: UploadFile = File(..., description="Food photograph (JPEG / PNG / WebP)"),
    current_user: UserPublic = Depends(get_current_user),
) -> ImageAnalysisResponse:
    """
    Upload a food photo and receive:

    - A list of detected food items with confidence scores and calorie estimates.
    - Total estimated calories for the meal.
    - Healthier swap suggestions with calorie difference and reasoning.
    - Nutritional notes and an overall AI explanation.

    **File limits:** max 10 MB — JPEG, PNG, or WebP.
    """
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="user_id in form must match the authenticated user.",
        )

    if image.content_type not in {"image/jpeg", "image/png", "image/webp", "image/gif"}:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only JPEG, PNG, WebP, and GIF images are accepted.",
        )

    image_data = await image.read()

    if len(image_data) > _MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Image exceeds the 10 MB size limit.",
        )

    try:
        result = analyse_food_image(image_data, image.content_type or "image/jpeg", current_user.id)
    except ValueError as exc:
        logger.error("Image analysis value error", user_id=current_user.id, error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except RuntimeError as exc:
        logger.error("Image analysis inference failure", user_id=current_user.id, error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The AI service is temporarily unavailable. Please try again.",
        ) from exc

    logger.info("Image analysis complete", user_id=current_user.id)
    return result
