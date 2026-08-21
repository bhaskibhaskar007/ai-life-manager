"""Reminder schemas."""

from pydantic import BaseModel, Field


class ReminderCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    due_date: str = Field(..., description="YYYY-MM-DD")
    due_time: str | None = Field(None, description="HH:MM (24-hour)")
    priority: str = Field("medium", description="low, medium, high")
    recurrence: str = Field("none", description="none, daily, weekly, monthly")


class ReminderUpdateRequest(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    due_date: str | None = None
    due_time: str | None = None
    priority: str | None = None
    recurrence: str | None = None


class ReminderResponse(BaseModel):
    id: int
    title: str
    description: str | None
    due_date: str
    due_time: str | None
    priority: str
    status: str
    recurrence: str
    is_overdue: bool
