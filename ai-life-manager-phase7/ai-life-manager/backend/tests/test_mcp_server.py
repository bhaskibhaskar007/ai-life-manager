"""
Verifies the FastMCP skeleton: tool discovery and in-process invocation.

Uses FastMCP's in-memory `Client` transport (no network/HTTP needed) —
this is the standard way to test a FastMCP server directly against the
`mcp` instance.
"""

import pytest
from fastmcp import Client

from app.mcp.server import mcp

# Import tool/resource/prompt modules so their decorators register
# before the test runs (create_mcp_app() normally does this at app
# startup; tests exercise `mcp` directly instead of the ASGI app).
import app.mcp.prompts  # noqa: F401,E402
import app.mcp.resources  # noqa: F401,E402
import app.mcp.tools  # noqa: F401,E402


@pytest.mark.asyncio
async def test_ping_tool_is_discoverable():
    async with Client(mcp) as client:
        tools = await client.list_tools()
        tool_names = {t.name for t in tools}
        assert "ping" in tool_names


@pytest.mark.asyncio
async def test_ping_tool_executes():
    async with Client(mcp) as client:
        result = await client.call_tool("ping", {})
        assert result.data["success"] is True
        assert "server_time_utc" in result.data


@pytest.mark.asyncio
async def test_financial_coach_prompt_is_discoverable():
    async with Client(mcp) as client:
        prompts = await client.list_prompts()
        prompt_names = {p.name for p in prompts}
        assert "financial_coach_prompt" in prompt_names


@pytest.mark.asyncio
async def test_user_context_resource_is_discoverable():
    async with Client(mcp) as client:
        templates = await client.list_resource_templates()
        uris = {t.uriTemplate for t in templates}
        assert "user://context/{user_id}" in uris
