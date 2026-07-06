"""Pydantic models for Nutrition Label Analysis."""

from typing import List, Optional

from pydantic import BaseModel, Field


class NutrientDetail(BaseModel):
    """A single nutrient entry parsed from a nutrition label."""

    name: str
    amount: str
    daily_value_percent: Optional[float] = None
    assessment: str


class LabelWarning(BaseModel):
    """A health warning derived from label analysis."""

    category: str
    message: str
    severity: str = Field(..., pattern="^(low|medium|high)$")


class LabelAnalysisResponse(BaseModel):
    """Full interpretation of an uploaded nutrition label."""

    product_name: Optional[str] = None
    serving_size: str
    calories_per_serving: int
    sugar: NutrientDetail
    fat: NutrientDetail
    protein: NutrientDetail
    sodium: NutrientDetail
    additional_nutrients: List[NutrientDetail] = Field(default_factory=list)
    warnings: List[LabelWarning]
    overall_assessment: str
    explanation: str
