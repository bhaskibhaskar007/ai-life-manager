"""
Chat REST endpoint.

Connects the user's conversational interface to the AIOrchestrator and FastMCP tools.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.auth.dependencies import get_current_user_optional
from app.models.user import User
from app.schemas.chat import ChatResponse
from app.services.ai_orchestrator import AIOrchestrator

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    user_id: int | None = Field(None, description="Explicit user_id (used when testing without JWT)")
    conversation_history: list[dict] | None = None


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatMessageRequest,
    current_user: User | None = Depends(get_current_user_optional),
) -> ChatResponse:
    effective_user_id = current_user.id if current_user else (request.user_id or 1)
    orchestrator = AIOrchestrator()
    result = await orchestrator.handle_message(
        user_id=effective_user_id,
        message=request.message,
        conversation_history=request.conversation_history,
    )
    return ChatResponse(**result)
