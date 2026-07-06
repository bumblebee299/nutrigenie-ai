"""Pydantic models for Food Swap recommendations."""

from typing import List

from pydantic import BaseModel


class FoodSwapRequest(BaseModel):
    """Input for the healthy food swap feature."""

    food_item: str
    user_id: str
    dietary_restrictions: List[str] = []


class SwapOption(BaseModel):
    """A single food swap suggestion."""

    original: str
    healthier_option: str
    calorie_reduction: int
    benefits: List[str]
    preparation_tip: str
    explanation: str


class FoodSwapResponse(BaseModel):
    """All swap suggestions for a given food item."""

    original_food: str
    swaps: List[SwapOption]
    general_advice: str
