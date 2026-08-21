"""
Importing this package registers every tool module onto the shared
`mcp` instance (each module's `@mcp.tool` decorators run on import).

Registered tool groups:
    expense, analytics, reminder, memory, weather, budget, planner, system
"""

from app.mcp.tools import analytics, budget, expense, memory, planner, reminder, system, weather  # noqa: F401

__all__ = ["system", "expense", "analytics", "reminder", "memory", "weather", "budget", "planner"]
