"""Request/response schemas for the /chat REST endpoint (plain REST, not MCP — see main.py comment)."""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    user_id: int
    message: str = Field(min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    response: str
    used_fallback: bool
    tools_called: list[str]
