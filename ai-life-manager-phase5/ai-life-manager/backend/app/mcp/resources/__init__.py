"""Importing this package registers every resource module onto the shared `mcp` instance."""

from app.mcp.resources import user_context  # noqa: F401

__all__ = ["user_context"]
