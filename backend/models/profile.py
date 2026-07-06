"""Pydantic models for User Profile."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field

from backend.models.meal_plan import Gender, GoalType, Lifestyle


class ProfileUpdate(BaseModel):
    """Payload for updating a user's profile."""

    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    age: Optional[int] = Field(default=None, ge=1, le=120)
    height_cm: Optional[float] = Field(default=None, ge=50, le=300)
    weight_kg: Optional[float] = Field(default=None, ge=10, le=500)
    gender: Optional[Gender] = None
    goal: Optional[GoalType] = None
    diseases: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    cuisine_preference: Optional[List[str]] = None
    lifestyle: Optional[Lifestyle] = None


class ProfileResponse(BaseModel):
    """Full user profile as returned to the client."""

    id: str
    name: str
    email: EmailStr
    age: Optional[int] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    gender: Optional[Gender] = None
    goal: Optional[GoalType] = None
    diseases: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    cuisine_preference: List[str] = Field(default_factory=list)
    lifestyle: Optional[Lifestyle] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
