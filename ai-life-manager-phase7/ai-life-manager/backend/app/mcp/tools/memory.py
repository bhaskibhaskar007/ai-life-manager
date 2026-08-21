"""
Memory MCP tools.

`save_user_preference` only accepts keys from a fixed allow-list (see
`MemoryService.ALLOWED_PREFERENCE_KEYS`) — this is what makes "never
store passwords or sensitive credentials" an enforced rule rather than
just a docstring instruction to the LLM.
"""

from app.database import AsyncSessionLocal
from app.mcp.logging import log_tool_execution
from app.mcp.server import mcp
from app.services.memory_service import MemoryService


@mcp.tool
@log_tool_execution("save_user_preference")
async def save_user_preference(user_id: int, key: str, value: str) -> dict:
    """
    Save a non-sensitive user preference (e.g. preferred currency,
    reminder style, common expense categories). Only a fixed set of
    keys is supported — passwords, tokens, or other credentials can
    never be saved through this tool. If you pass an unsupported key,
    the error message lists what IS supported.
    """
    async with AsyncSessionLocal() as session:
        service = MemoryService(session)
        result = await service.save_user_preference(user_id=user_id, key=key, value=value)
        return {"success": True, "preference": result}


@mcp.tool
@log_tool_execution("get_user_preference")
async def get_user_preference(user_id: int, key: str) -> dict:
    """Retrieve a previously saved user preference by key. Returns found=False if never set."""
    async with AsyncSessionLocal() as session:
        service = MemoryService(session)
        result = await service.get_user_preference(user_id=user_id, key=key)
        return {"success": True, **result}


@mcp.tool
@log_tool_execution("save_user_context")
async def save_user_context(user_id: int, summary: str) -> dict:
    """
    Save a short, non-sensitive summary of something worth remembering
    about this conversation or the user's habits (e.g. "user usually
    asks about weekly spending on Mondays"). Never save passwords,
    tokens, or other sensitive personal data here — this is for
    lightweight behavioral/preference context only, not a transcript store.
    """
    async with AsyncSessionLocal() as session:
        service = MemoryService(session)
        result = await service.save_user_context(user_id=user_id, summary=summary)
        return {"success": True, "context": result}


@mcp.tool
@log_tool_execution("retrieve_relevant_context")
async def retrieve_relevant_context(user_id: int, query: str | None = None, limit: int = 5) -> dict:
    """
    Retrieve previously saved context summaries for this user. If
    `query` is given, does a keyword match against saved summaries;
    otherwise returns the most recent ones (default 5, max 20).
    """
    async with AsyncSessionLocal() as session:
        service = MemoryService(session)
        results = await service.retrieve_relevant_context(user_id=user_id, query=query, limit=limit)
        return {"success": True, "count": len(results), "context": results}
