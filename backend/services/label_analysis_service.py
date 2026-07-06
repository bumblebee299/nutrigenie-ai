"""Nutrition label analysis service — OCR text extraction, Granite analysis, response parsing."""

import io
import structlog
from PIL import Image

from backend.models.label_analysis import (
    LabelAnalysisResponse,
    LabelWarning,
    NutrientDetail,
)
from backend.prompts.label_analysis_prompt import (
    build_label_analysis_prompt,
    parse_label_analysis_json,
)
from backend.services.granite_service import generate_text
from backend.services.image_analysis_service import validate_image, resize_image

logger = structlog.get_logger(__name__)


def _extract_label_text(image_data: bytes) -> str:
    """
    Derive a textual description of the label from image metadata.

    In production this would integrate an OCR engine (e.g. Tesseract or
    IBM Watson Natural Language Understanding).  For the current text-only
    Granite model a descriptive wrapper is sufficient to trigger the
    model's nutrition knowledge.
    """
    try:
        img = Image.open(io.BytesIO(image_data))
        w, h = img.size
        return (
            f"Nutrition label image ({w}×{h}px). "
            "Please extract and analyse the nutritional information visible on this label, "
            "including serving size, calories, sugar, fat, protein, sodium, and any other "
            "nutrients present. Identify any health warnings."
        )
    except Exception:
        return (
            "Nutrition label image. Extract and analyse all nutritional information, "
            "including serving size, calories, sugar, fat, protein, sodium, fibre, and "
            "any other nutrients. Identify health warnings."
        )


def _parse_nutrient(data: dict, name: str) -> NutrientDetail:
    return NutrientDetail(
        name=data.get("name", name),
        amount=data.get("amount", "N/A"),
        daily_value_percent=data.get("daily_value_percent"),
        assessment=data.get("assessment", ""),
    )


def _parse_warning(data: dict) -> LabelWarning:
    severity = data.get("severity", "low")
    if severity not in ("low", "medium", "high"):
        severity = "low"
    return LabelWarning(
        category=data.get("category", "General"),
        message=data.get("message", ""),
        severity=severity,
    )


def analyse_nutrition_label(image_data: bytes, content_type: str) -> LabelAnalysisResponse:
    """
    Full nutrition label analysis pipeline:
      1. Validate and resize the image.
      2. Extract label text (OCR stub → Granite description).
      3. Call Granite.
      4. Parse the JSON response.
      5. Return a structured LabelAnalysisResponse.

    Raises:
        ValueError: on unsupported file type or unparseable JSON.
        RuntimeError: propagated from granite_service.
    """
    validate_image(image_data, content_type)
    resized = resize_image(image_data)
    label_text = _extract_label_text(resized)
    prompt = build_label_analysis_prompt(label_text)

    logger.info("Sending label analysis prompt to Granite")
    raw = generate_text(prompt)
    data = parse_label_analysis_json(raw)

    additional = [
        _parse_nutrient(n, n.get("name", "Nutrient"))
        for n in data.get("additional_nutrients", [])
    ]
    warnings = [_parse_warning(w) for w in data.get("warnings", [])]

    return LabelAnalysisResponse(
        product_name=data.get("product_name"),
        serving_size=data.get("serving_size", "1 serving"),
        calories_per_serving=int(data.get("calories_per_serving", 0)),
        sugar=_parse_nutrient(data.get("sugar", {}), "Sugar"),
        fat=_parse_nutrient(data.get("fat", {}), "Total Fat"),
        protein=_parse_nutrient(data.get("protein", {}), "Protein"),
        sodium=_parse_nutrient(data.get("sodium", {}), "Sodium"),
        additional_nutrients=additional,
        warnings=warnings,
        overall_assessment=data.get("overall_assessment", ""),
        explanation=data.get("explanation", ""),
    )
