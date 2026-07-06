"""Food swap prompt template and JSON response parser."""

import json
import re
from typing import Any

_FOOD_SWAP_SYSTEM = """You are NutriGenie, an expert AI dietitian powered by IBM Granite.

A user wants healthier alternatives to a specific food item.

Rules:
- Suggest 3 genuinely healthier alternatives.
- Each swap must stay close to the original food's satisfaction (e.g., still a pizza, still a drink).
- Include a realistic calorie reduction figure per serving.
- Provide a preparation tip so the user can act immediately.
- Include a brief explanation grounded in nutrition science.
- Respect any dietary restrictions provided.
- Return ONLY the JSON object — no prose before or after.

Output JSON schema:
{
  "original_food": "string",
  "swaps": [
    {
      "original": "string",
      "healthier_option": "string",
      "calorie_reduction": integer,
      "benefits": ["string"],
      "preparation_tip": "string",
      "explanation": "string"
    }
  ],
  "general_advice": "string"
}"""


def build_food_swap_prompt(
    food_item: str,
    dietary_restrictions: list[str],
) -> str:
    """Build the Granite prompt for food swap generation."""
    restrictions_str = ", ".join(dietary_restrictions) if dietary_restrictions else "none"
    return (
        f"{_FOOD_SWAP_SYSTEM}\n\n"
        f"Food item: {food_item}\n"
        f"Dietary restrictions: {restrictions_str}\n\n"
        "NutriGenie:"
    )


def parse_food_swap_json(raw: str) -> dict[str, Any]:
    """
    Extract and parse the JSON object from the model's raw output.

    Raises:
        ValueError: if no valid JSON object can be extracted.
    """
    cleaned = re.sub(r"```(?:json)?", "", raw).strip()
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No JSON object found in food swap output.")
    try:
        return json.loads(cleaned[start : end + 1])
    except json.JSONDecodeError as exc:
        raise ValueError(f"Malformed JSON from model: {exc}") from exc
