"""Pydantic models for Food Image Analysis."""

from typing import List, Optional

from pydantic import BaseModel, Field


class FoodItem(BaseModel):
    """A food item detected in an image."""

    name: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    estimated_calories: int
    portion_size: str


class HealthierAlternative(BaseModel):
    """A suggested healthier food swap."""

    original: str
    alternative: str
    reason: str
    calorie_difference: int


class ImageAnalysisResponse(BaseModel):
    """Analysis result for an uploaded food image."""

    detected_foods: List[FoodItem]
    total_estimated_calories: int
    healthier_alternatives: List[HealthierAlternative]
    nutritional_notes: str
    explanation: str
    image_url: Optional[str] = None
