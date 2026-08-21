"""
MCP resources.

Resources are read-only, addressable data the LLM can pull into context
without calling a "tool" — think of them as GET endpoints for the MCP
protocol. `user_context` exposes a lightweight profile (currency
preference, active budgets count, etc.) that tools like `plan_day` or
`generate_financial_insight` can reference. Full implementation lands
in Phase 8 (Memory/Context) — this is a working stub so the resource
is discoverable and the shape is settled early.
"""

from app.mcp.server import mcp


@mcp.resource("user://context/{user_id}")
async def get_user_context(user_id: str) -> dict:
    """
    Lightweight context summary for a user. Real data (currency
    preference, recent context summaries, common categories) is wired
    up in Phase 8 once the memory service exists — for now this
    returns a stub shape so downstream tools can be written against a
    stable contract.
    """
    return {
        "user_id": user_id,
        "currency": "INR",
        "note": "Stub resource — full user context wired up in Phase 8 (Memory/Context tools).",
    }
