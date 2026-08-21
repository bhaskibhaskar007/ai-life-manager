"""
The single, shared FastMCP server instance for AI Life Manager.

Design note: tool/resource/prompt modules import `mcp` from *this* file
and decorate their functions with `@mcp.tool`, `@mcp.resource(...)`, or
`@mcp.prompt`. Nothing is registered until those modules are actually
imported — which is why `app/mcp/tools/__init__.py`,
`app/mcp/resources/__init__.py`, and `app/mcp/prompts/__init__.py`
import every module in their package. `create_mcp_app()` triggers all
of that by importing the three packages, then returns the mounted
ASGI app.
"""

from fastmcp import FastMCP

mcp = FastMCP(
    name="AI Life Manager",
    instructions=(
        "Tools for managing personal expenses, budgets, reminders, and "
        "daily planning. Prefer the most specific tool for the user's "
        "intent (e.g. use get_expense_summary for 'how much did I spend', "
        "not get_expenses). All amounts are in the user's preferred "
        "currency unless stated otherwise. Never fabricate data — if a "
        "tool returns no results, say so plainly."
    ),
)


def create_mcp_app():
    """
    Import every tool/resource/prompt module (registering them onto
    `mcp` as a side effect), then return the ASGI app to be mounted
    onto the main FastAPI app.
    """
    import app.mcp.prompts  # noqa: F401
    import app.mcp.resources  # noqa: F401
    import app.mcp.tools  # noqa: F401

    return mcp.http_app(path="/", transport="streamable-http")
