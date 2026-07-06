"""Meal plan prompt template and structured-output parser."""

import json
import re
from typing import Any

_MEAL_PLAN_SYSTEM = """You are NutriGenie, an expert AI dietitian powered by IBM Granite.

Generate a complete, personalised one-day meal plan in strict JSON format.

Rules:
- All meals must respect the user's allergies and dietary restrictions.
- Respect the cuisine preference when specified.
- Stay within the daily calorie target (±50 kcal is acceptable).
- Every meal must include a short explanation of why it was chosen.
- Return ONLY the JSON object — no prose before or after it.
- Use metric units (grams, ml).

Output JSON schema:
{
  "breakfast": {
    "name": "string",
    "ingredients": ["string"],
    "calories": integer,
    "protein_g": float,
    "carbs_g": float,
    "fat_g": float,
    "preparation_time_minutes": integer,
    "instructions": "string",
    "explanation": "string"
  },
  "lunch": { ... same fields ... },
  "dinner": { ... same fields ... },
  "snacks": [{ ... same fields ... }],
  "nutrition_summary": {
    "total_calories": integer,
    "protein_g": float,
    "carbs_g": float,
    "fat_g": float,
    "fiber_g": float,
    "water_ml": integer
  },
  "explanation": "string — overall rationale for this plan"
}"""


def build_meal_plan_prompt(
    age: int,
    height_cm: float,
    weight_kg: float,
    gender: str,
    goal: str,
    diseases: list[str],
    allergies: list[str],
    cuisine_preference: list[str],
    budget_usd_per_day: float | None,
    lifestyle: str,
    target_calories: int,
) -> str:
    """Construct the full Granite prompt for meal plan generation."""
    allergy_str = ", ".join(allergies) if allergies else "none"
    disease_str = ", ".join(diseases) if diseases else "none"
    cuisine_str = ", ".join(cuisine_preference) if cuisine_preference else "any"
    budget_str = f"${budget_usd_per_day:.0f}/day" if budget_usd_per_day else "no constraint"

    user_block = f"""User profile:
- Age: {age} years
- Height: {height_cm} cm
- Weight: {weight_kg} kg
- Gender: {gender}
- Goal: {goal.replace("_", " ")}
- Medical conditions: {disease_str}
- Allergies: {allergy_str}
- Cuisine preference: {cuisine_str}
- Budget: {budget_str}
- Lifestyle: {lifestyle.replace("_", " ")}
- Daily calorie target: {target_calories} kcal

Generate the one-day meal plan now:"""

    return f"{_MEAL_PLAN_SYSTEM}\n\n{user_block}\nNutriGenie:"


def parse_meal_plan_json(raw: str) -> dict[str, Any]:
    """
    Extract and parse the JSON object from the model's raw output.

    The model may wrap the JSON in prose or markdown code fences —
    this function handles all common formats.

    Raises:
        ValueError: if no valid JSON object can be extracted.
    """
    # Strip markdown code fences if present
    cleaned = re.sub(r"```(?:json)?", "", raw).strip()

    # Find the first { ... } block
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No JSON object found in model output.")

    json_str = cleaned[start : end + 1]
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Malformed JSON from model: {exc}") from exc
