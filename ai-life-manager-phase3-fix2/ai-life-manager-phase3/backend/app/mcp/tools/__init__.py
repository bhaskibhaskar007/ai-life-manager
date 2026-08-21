"""
Importing this package registers every tool module onto the shared
`mcp` instance (each module's `@mcp.tool` decorators run on import).

Add new tool modules' imports here as they're built in later phases:
    Phase 5: expense
    Phase 6: analytics
    Phase 7: reminder
    Phase 8: memory
    Phase 9: weather, budget
"""

from app.mcp.tools import system  # noqa: F401

__all__ = ["system"]
