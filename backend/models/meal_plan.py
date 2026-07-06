"""Pydantic models for Meal Planning."""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class GoalType(str, Enum):
    WEIGHT_LOSS = "weight_loss"
    WEIGHT_GAIN = "weight_gain"
    MAINTENANCE = "maintenance"
    MUSCLE_GAIN = "muscle_gain"


class Lifestyle(str, Enum):
    SEDENTARY = "sedentary"
    LIGHTLY_ACTIVE = "lightly_active"
    MODERATELY_ACTIVE = "moderately_active"
    VERY_ACTIVE = "very_active"
    EXTRA_ACTIVE = "extra_active"


class Meal(BaseModel):
    """A single meal entry within a plan."""

    name: str
    ingredients: List[str]
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    preparation_time_minutes: int
    instructions: str
    explanation: str


class MealPlanRequest(BaseModel):
    """Input profile used to generate a personalised meal plan."""

    user_id: str
    age: int = Field(..., ge=1, le=120)
    height_cm: float = Field(..., ge=50, le=300)
    weight_kg: float = Field(..., ge=10, le=500)
    gender: Gender
    goal: GoalType
    diseases: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    cuisine_preference: List[str] = Field(default_factory=list)
    budget_usd_per_day: Optional[float] = Field(default=None, ge=1)
    lifestyle: Lifestyle


class DailyNutritionSummary(BaseModel):
    """Aggregated nutrition figures for a full day."""

    total_calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float
    water_ml: int


class MealPlanResponse(BaseModel):
    """Complete personalised meal plan returned by the API."""

    user_id: str
    breakfast: Meal
    lunch: Meal
    dinner: Meal
    snacks: List[Meal]
    nutrition_summary: DailyNutritionSummary
    explanation: str
