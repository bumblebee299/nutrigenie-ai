"""Nutrition Label Analysis route."""

import structlog
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from backend.api.dependencies import get_current_user
from backend.models.auth import UserPublic
from backend.models.label_analysis import LabelAnalysisResponse
from backend.services.label_analysis_service import analyse_nutrition_label

logger = structlog.get_logger(__name__)
router = APIRouter()

_MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post(
    "/",
    response_model=LabelAnalysisResponse,
    summary="Analyse an uploaded nutrition label image",
    status_code=status.HTTP_200_OK,
)
async def analyse_label(
    user_id: str = Form(...),
    label_image: UploadFile = File(...),
    current_user: UserPublic = Depends(get_current_user),
) -> LabelAnalysisResponse:
    """
    Upload a nutrition label photograph and receive a plain-English breakdown of:

    - **Sugar** — amount, % daily value, health assessment
    - **Fat** — total fat content and assessment
    - **Protein** — protein content and assessment
    - **Sodium** — sodium content with warnings if high
    - Additional nutrients (fibre, vitamins, etc.)
    - Health warnings with severity levels (low / medium / high)
    - An overall nutritional assessment and explanation
    """
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="user_id in form must match the authenticated user.",
        )

    if label_image.content_type not in {"image/jpeg", "image/png", "image/webp", "image/gif"}:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only JPEG, PNG, WebP, and GIF images are accepted.",
        )

    image_data = await label_image.read()

    if len(image_data) > _MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Image exceeds the 10 MB size limit.",
        )

    try:
        result = analyse_nutrition_label(image_data, label_image.content_type or "image/jpeg")
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The AI service is temporarily unavailable. Please try again.",
        ) from exc

    logger.info("Label analysis complete", user_id=current_user.id)
    return result
