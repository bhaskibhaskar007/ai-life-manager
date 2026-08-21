"""
Importing this package registers every tool module onto the shared
`mcp` instance (each module's `@mcp.tool` decorators run on import).

All 8 planned tool groups are now wired up:
    expense, analytics, reminder, memory, weather, budget, system
"""

from app.mcp.tools import analytics, budget, expense, memory, reminder, system, weather  # noqa: F401

__all__ = ["system", "expense", "analytics", "reminder", "memory", "weather", "budget"]
