"""
Chat REST endpoint.

This is plain REST, not MCP — the person's browser talks REST to this
endpoint; this endpoint's handler is what opens an MCP *client*
connection to our own MCP server internally (see AIOrchestrator).
Authentication (resolving a real user_id from a JWT instead of trusting
a client-supplied one) is added in Phase 13.
"""

from fastapi import APIRouter

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.ai_orchestrator import AIOrchestrator

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    orchestrator = AIOrchestrator()
    result = await orchestrator.handle_message(user_id=request.user_id, message=request.message)
    return ChatResponse(**result)
