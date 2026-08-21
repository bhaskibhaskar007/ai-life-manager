"""
System-level MCP tools.

`ping` is intentionally trivial: it exists so we can verify tool
discovery and invocation work end-to-end (Phase 3) before any real
business logic (expenses, reminders, ...) is added in later phases.
"""

from datetime import datetime, timezone

from app.mcp.logging import log_tool_execution
from app.mcp.server import mcp


@mcp.tool
@log_tool_execution("ping")
async def ping(user_id: int | None = None) -> dict:
    """
    Health-check tool for the MCP layer itself. Returns the current
    server time. Useful for confirming the MCP client can discover and
    call tools before wiring up real functionality.
    """
    return {
        "success": True,
        "message": "AI Life Manager MCP server is reachable.",
        "server_time_utc": datetime.now(timezone.utc).isoformat(),
    }
