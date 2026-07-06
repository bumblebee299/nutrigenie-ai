"""Image analysis service — COS upload, Granite inference, response parsing."""

import uuid
from datetime import datetime, timezone

import structlog
from PIL import Image
import io

from backend.api.config import settings
from backend.database.cos import cos_client
from backend.models.image_analysis import (
    FoodItem,
    HealthierAlternative,
    ImageAnalysisResponse,
)
from backend.prompts.image_analysis_prompt import (
    build_image_analysis_prompt,
    parse_image_analysis_json,
)
from backend.services.granite_service import generate_text

logger = structlog.get_logger(__name__)

# Maximum image dimensions before downscaling (preserves API payload size)
_MAX_DIM = 1024
# Supported MIME types
_ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}


def validate_image(data: bytes, content_type: str) -> None:
    """
    Reject files that are not supported image types.

    Raises:
        ValueError: if the content type is not an accepted image format.
    """
    if content_type not in _ALLOWED_TYPES:
        raise ValueError(
            f"Unsupported file type '{content_type}'. "
            f"Accepted types: {', '.join(sorted(_ALLOWED_TYPES))}."
        )


def resize_image(data: bytes) -> bytes:
    """
    Downscale the image to fit within _MAX_DIM × _MAX_DIM while preserving
    aspect ratio. Returns the original bytes if already within bounds.
    """
    img = Image.open(io.BytesIO(data))
    if img.width <= _MAX_DIM and img.height <= _MAX_DIM:
        return data

    img.thumbnail((_MAX_DIM, _MAX_DIM), Image.LANCZOS)
    buffer = io.BytesIO()
    fmt = img.format or "JPEG"
    img.save(buffer, format=fmt)
    return buffer.getvalue()


def upload_image_to_cos(image_data: bytes, content_type: str, user_id: str) -> str:
    """
    Upload the image to IBM Cloud Object Storage.

    Returns:
        The public-accessible URL of the uploaded object.
    """
    key = f"food-images/{user_id}/{uuid.uuid4()}.jpg"
    cos_client.put_object(
        Bucket=settings.COS_BUCKET_IMAGES,
        Key=key,
        Body=image_data,
        ContentType=content_type,
    )
    url = f"{settings.COS_ENDPOINT}/{settings.COS_BUCKET_IMAGES}/{key}"
    logger.info("Image uploaded to COS", key=key, user_id=user_id)
    return url


def _build_image_description(image_data: bytes) -> str:
    """
    Produce a textual description of the image for the text-only Granite model.

    For production deployments with a multimodal model, this function can be
    replaced with a direct base64 vision API call.  For the current Granite
    text model the description is derived from image metadata and a fixed
    prompt that instructs the model to reason about the food content.
    """
    try:
        img = Image.open(io.BytesIO(image_data))
        mode = img.mode
        width, height = img.size
        return (
            f"A food photograph ({width}×{height}px, {mode} colour space). "
            "Please identify all visible food items, estimate their portions "
            "and calories, and suggest healthier alternatives."
        )
    except Exception:
        return (
            "A food photograph. Please identify all visible food items, "
            "estimate their portions and calories, and suggest healthier alternatives."
        )


def _parse_food_item(data: dict) -> FoodItem:
    return FoodItem(
        name=data.get("name", "Unknown food"),
        confidence=float(data.get("confidence", 0.8)),
        estimated_calories=int(data.get("estimated_calories", 0)),
        portion_size=data.get("portion_size", "1 serving"),
    )


def _parse_alternative(data: dict) -> HealthierAlternative:
    return HealthierAlternative(
        original=data.get("original", ""),
        alternative=data.get("alternative", ""),
        reason=data.get("reason", ""),
        calorie_difference=int(data.get("calorie_difference", 0)),
    )


def analyse_food_image(image_data: bytes, content_type: str, user_id: str) -> ImageAnalysisResponse:
    """
    Full food image analysis pipeline:

    1. Validate and resize the uploaded image.
    2. Upload original to IBM COS.
    3. Build a textual description for Granite.
    4. Call Granite and parse the JSON response.
    5. Return a structured ImageAnalysisResponse.

    Raises:
        ValueError: on unsupported file type or unparseable JSON.
        RuntimeError: propagated from granite_service on inference failure.
    """
    validate_image(image_data, content_type)
    resized = resize_image(image_data)
    image_url = upload_image_to_cos(resized, content_type, user_id)

    description = _build_image_description(image_data)
    prompt = build_image_analysis_prompt(description)

    logger.info("Sending image analysis prompt to Granite", user_id=user_id)
    raw_output = generate_text(prompt)
    parsed = parse_image_analysis_json(raw_output)

    detected_foods = [_parse_food_item(f) for f in parsed.get("detected_foods", [])]
    alternatives = [_parse_alternative(a) for a in parsed.get("healthier_alternatives", [])]

    return ImageAnalysisResponse(
        detected_foods=detected_foods,
        total_estimated_calories=int(parsed.get("total_estimated_calories", 0)),
        healthier_alternatives=alternatives,
        nutritional_notes=parsed.get("nutritional_notes", ""),
        explanation=parsed.get("explanation", ""),
        image_url=image_url,
    )
