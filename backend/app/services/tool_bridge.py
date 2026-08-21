"""
Converts MCP tool definitions (from an MCP `Client.list_tools()` call)
into Anthropic's `tools=[...]` parameter format.

Both are JSON Schema underneath, so this is mostly about grabbing the
right attribute name — MCP's wire format uses `inputSchema` (per the
protocol spec), but different client library versions have exposed it
as either `inputSchema` or the more Pythonic `input_schema`. Checking
both defensively means this doesn't silently break on a fastmcp
version bump.
"""

from typing import Any


def _extract_input_schema(tool: Any) -> dict:
    for attr in ("inputSchema", "input_schema"):
        schema = getattr(tool, attr, None)
        if schema:
            return schema
    return {"type": "object", "properties": {}}


def mcp_tool_to_anthropic_schema(tool: Any) -> dict:
    return {
        "name": tool.name,
        "description": tool.description or "",
        "input_schema": _extract_input_schema(tool),
    }


async def get_anthropic_tools(mcp_client: Any) -> list[dict]:
    """`mcp_client` is an already-connected fastmcp `Client` (async context manager entered)."""
    tools = await mcp_client.list_tools()
    return [mcp_tool_to_anthropic_schema(t) for t in tools]
