"""Pydantic models for AI Chat."""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    """A single message in a chat conversation."""

    role: MessageRole
    content: str = Field(..., min_length=1, max_length=4096)
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    """Request payload for the chat endpoint."""

    message: str = Field(..., min_length=1, max_length=4096)
    history: List[ChatMessage] = Field(default_factory=list, max_length=20)
    user_id: str


class ChatResponse(BaseModel):
    """Response from the AI chat endpoint."""

    reply: str
    explanation: str
    sources: List[str] = Field(default_factory=list)
    timestamp: datetime


class FeedbackRequest(BaseModel):
    """User feedback on an AI recommendation."""

    message_id: str
    helpful: bool
    comment: Optional[str] = Field(default=None, max_length=500)
    user_id: str
