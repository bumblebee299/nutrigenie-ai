"""Image Analysis prompt template and response parser."""

import json
import re
from typing import Any

_IMAGE_ANALYSIS_SYSTEM = """You are NutriGenie, an expert AI food recognition and nutrition analyst powered by IBM Granite.

You have been given a food image. Analyse it and respond in strict JSON format.

Rules:
- Identify every distinct food item visible in the image.
- Estimate portion sizes realistically (e.g. "1 medium apple", "200g cooked rice").
- Calorie estimates must be realistic and evidence-based.
- Suggest 1–3 genuinely healthier alternatives per detected food.
- Every alternative must state the calorie difference and the reason.
- Return ONLY the JSON object — no prose before or after.

Output JSON schema:
{
  "detected_foods": [
    {
      "name": "string",
      "confidence": float (0.0–1.0),
      "estimated_calories": integer,
      "portion_size": "string"
    }
  ],
  "total_estimated_calories": integer,
  "healthier_alternatives": [
    {
      "original": "string",
      "alternative": "string",
      "reason": "string",
      "calorie_difference": integer
    }
  ],
  "nutritional_notes": "string — key nutritional observations about the meal",
  "explanation": "string — overall assessment and recommendation"
}"""


def build_image_analysis_prompt(image_description: str) -> str:
    """
    Build the Granite prompt for food image analysis.

    Args:
        image_description: A textual description of the image content
                           produced by a vision pre-processing step or
                           passed directly for text-only Granite models.

    Returns:
        Formatted prompt string.
    """
    return (
        f"{_IMAGE_ANALYSIS_SYSTEM}\n\n"
        f"Image content: {image_description}\n\n"
        "NutriGenie:"
    )


def parse_image_analysis_json(raw: str) -> dict[str, Any]:
    """
    Extract and parse the JSON object from the model's raw output.

    Raises:
        ValueError: if no valid JSON object can be extracted.
    """
    cleaned = re.sub(r"```(?:json)?", "", raw).strip()
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No JSON object found in image analysis output.")
    json_str = cleaned[start : end + 1]
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Malformed JSON from model: {exc}") from exc
