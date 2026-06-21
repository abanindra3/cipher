from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    conversation_id: int | None = None


class ChatResponse(BaseModel):
    conversation_id: int
    response: str
    tool_results: list[dict[str, Any]] = []
    remembered: list[dict[str, str]] = []


class ToolRequest(BaseModel):
    name: str
    arguments: dict[str, Any] = {}
    confirmed: bool = False


class MemoryUpsert(BaseModel):
    key: str
    value: str
    source: str = "user"
    confidence: float = 1.0


class NotificationRequest(BaseModel):
    channel: str
    title: str
    body: str
    speak: bool = False


class ReminderRequest(BaseModel):
    text: str
    due_at: datetime

