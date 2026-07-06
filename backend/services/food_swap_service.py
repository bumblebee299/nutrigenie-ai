"""Food swap service — Granite generation and response parsing."""

import structlog

from backend.models.food_swap import FoodSwapRequest, FoodSwapResponse, SwapOption
from backend.prompts.food_swap_prompt import build_food_swap_prompt, parse_food_swap_json
from backend.services.granite_service import generate_text

logger = structlog.get_logger(__name__)


def _parse_swap(data: dict) -> SwapOption:
    return SwapOption(
        original=data.get("original", ""),
        healthier_option=data.get("healthier_option", ""),
        calorie_reduction=int(data.get("calorie_reduction", 0)),
        benefits=data.get("benefits", []),
        preparation_tip=data.get("preparation_tip", ""),
        explanation=data.get("explanation", ""),
    )


def suggest_food_swaps(request: FoodSwapRequest) -> FoodSwapResponse:
    """
    Full food swap pipeline:
      1. Build the Granite prompt.
      2. Call Granite.
      3. Parse and validate the JSON response.
      4. Return a FoodSwapResponse.

    Raises:
        ValueError: if the model returns unparseable JSON.
        RuntimeError: propagated from granite_service on inference failure.
    """
    prompt = build_food_swap_prompt(
        food_item=request.food_item,
        dietary_restrictions=request.dietary_restrictions,
    )

    logger.info("Requesting food swaps from Granite", food_item=request.food_item)
    raw = generate_text(prompt)
    data = parse_food_swap_json(raw)

    return FoodSwapResponse(
        original_food=data.get("original_food", request.food_item),
        swaps=[_parse_swap(s) for s in data.get("swaps", [])],
        general_advice=data.get("general_advice", ""),
    )
