"""Pydantic models for Authentication."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    """Payload for user registration."""

    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class UserLogin(BaseModel):
    """Payload for user login."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT token pair returned after successful authentication."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefreshRequest(BaseModel):
    """Payload to exchange a refresh token for a new access token."""

    refresh_token: str


class UserPublic(BaseModel):
    """Safe user representation returned to clients."""

    id: str
    name: str
    email: EmailStr
    created_at: datetime
    is_active: bool = True
