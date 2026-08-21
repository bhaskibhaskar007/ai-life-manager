"""User preference schemas."""

from pydantic import BaseModel, Field


class PreferenceCreateRequest(BaseModel):
    key: str = Field(..., min_length=1, max_length=100)
    value: str = Field(..., min_length=1, max_length=500)


class PreferenceResponse(BaseModel):
    key: str
    value: str
    updated_at: str
