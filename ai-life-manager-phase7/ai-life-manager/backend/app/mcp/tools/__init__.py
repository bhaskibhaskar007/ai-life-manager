"""
Importing this package registers every tool module onto the shared
`mcp` instance (each module's `@mcp.tool` decorators run on import).

Add new tool modules' imports here as they're built in later phases:
    Phase 8: weather, budget
"""

from app.mcp.tools import analytics, expense, memory, reminder, system  # noqa: F401

__all__ = ["system", "expense", "analytics", "reminder", "memory"]
