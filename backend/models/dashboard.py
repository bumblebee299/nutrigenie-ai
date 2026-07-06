"""Pydantic models for the Weekly Progress Dashboard."""

from datetime import date
from typing import List, Optional

from pydantic import BaseModel


class DailyEntry(BaseModel):
    """A single day's tracked values."""

    date: date
    calories_consumed: int
    protein_g: float
    water_ml: int
    weight_kg: Optional[float] = None
    meals: Optional[List[dict]] = None
    feedback_rating: Optional[int] = None
    feedback_comment: Optional[str] = None


class WeeklySummary(BaseModel):
    """Aggregated statistics over a 7-day window."""

    avg_calories: float
    avg_protein_g: float
    avg_water_ml: float
    weight_change_kg: Optional[float] = None
    goal_adherence_percent: float


class GoalTargets(BaseModel):
    """Calorie, protein, and water targets."""

    calorie_target: int
    protein_target_g: float
    water_target_ml: int


class DashboardResponse(BaseModel):
    """Full weekly dashboard payload."""

    user_id: str
    week_start: date
    week_end: date
    daily_entries: List[DailyEntry]
    summary: WeeklySummary
    charts_data: dict  # Raw series data for recharts
    goals: Optional[GoalTargets] = None


class LogMealRequest(BaseModel):
    """Request payload to add a meal."""

    date: date
    type: str  # e.g., "breakfast", "lunch", "dinner", "snack"
    name: str
    calories: int
    protein_g: float


class LogWaterRequest(BaseModel):
    """Request payload to track water intake."""

    date: date
    amount_ml: int


class LogWeightRequest(BaseModel):
    """Request payload to log weight."""

    date: date
    weight_kg: float


class LogFeedbackRequest(BaseModel):
    """Request payload to submit daily feedback."""

    date: date
    rating: int  # 1 to 5 stars
    comment: Optional[str] = None
