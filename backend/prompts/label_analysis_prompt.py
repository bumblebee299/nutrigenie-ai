"""Nutrition label analysis prompt template and JSON response parser."""

import json
import re
from typing import Any

_LABEL_ANALYSIS_SYSTEM = """You are NutriGenie, an expert AI nutrition label analyst powered by IBM Granite.

You have been given text extracted from a nutrition label. Analyse it and respond in strict JSON format.

Rules:
- Extract and explain each key nutrient: sugar, fat (total), protein, and sodium.
- Flag high values as warnings with severity: low | medium | high.
- Assess overall nutritional quality in plain language.
- Keep explanations accessible to a general audience.
- Return ONLY the JSON object — no prose before or after.

Output JSON schema:
{
  "product_name": "string or null",
  "serving_size": "string",
  "calories_per_serving": integer,
  "sugar": {
    "name": "Sugar",
    "amount": "string (e.g. 12g)",
    "daily_value_percent": float or null,
    "assessment": "string"
  },
  "fat": {
    "name": "Total Fat",
    "amount": "string",
    "daily_value_percent": float or null,
    "assessment": "string"
  },
  "protein": {
    "name": "Protein",
    "amount": "string",
    "daily_value_percent": float or null,
    "assessment": "string"
  },
  "sodium": {
    "name": "Sodium",
    "amount": "string",
    "daily_value_percent": float or null,
    "assessment": "string"
  },
  "additional_nutrients": [
    {
      "name": "string",
      "amount": "string",
      "daily_value_percent": float or null,
      "assessment": "string"
    }
  ],
  "warnings": [
    {
      "category": "string",
      "message": "string",
      "severity": "low | medium | high"
    }
  ],
  "overall_assessment": "string",
  "explanation": "string — why this matters for the user's health"
}"""


def build_label_analysis_prompt(label_text: str) -> str:
    """Build the Granite prompt for nutrition label analysis."""
    return (
        f"{_LABEL_ANALYSIS_SYSTEM}\n\n"
        f"Nutrition label text:\n{label_text}\n\n"
        "NutriGenie:"
    )


def parse_label_analysis_json(raw: str) -> dict[str, Any]:
    """
    Extract and parse the JSON object from the model's raw output.

    Raises:
        ValueError: if no valid JSON object can be extracted.
    """
    cleaned = re.sub(r"```(?:json)?", "", raw).strip()
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No JSON object found in label analysis output.")
    try:
        return json.loads(cleaned[start : end + 1])
    except json.JSONDecodeError as exc:
        raise ValueError(f"Malformed JSON from model: {exc}") from exc
