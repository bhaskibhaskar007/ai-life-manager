"""Importing this package registers every prompt module onto the shared `mcp` instance."""

from app.mcp.prompts import financial_coach  # noqa: F401

__all__ = ["financial_coach"]
