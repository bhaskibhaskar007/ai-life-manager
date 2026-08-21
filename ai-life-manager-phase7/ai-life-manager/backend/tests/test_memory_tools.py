"""Tests for the memory MCP tools, run through FastMCP's in-memory Client."""

import pytest
from fastmcp import Client

from app.mcp.server import mcp

import app.mcp.prompts  # noqa: F401,E402
import app.mcp.resources  # noqa: F401,E402
import app.mcp.tools  # noqa: F401,E402


@pytest.mark.asyncio
async def test_save_and_get_preference(test_user_id):
    async with Client(mcp) as client:
        saved = await client.call_tool(
            "save_user_preference", {"user_id": test_user_id, "key": "currency", "value": "USD"}
        )
        assert saved.data["success"] is True
        assert saved.data["preference"]["value"] == "USD"

        fetched = await client.call_tool("get_user_preference", {"user_id": test_user_id, "key": "currency"})
        assert fetched.data["found"] is True
        assert fetched.data["value"] == "USD"


@pytest.mark.asyncio
async def test_save_preference_upserts_not_duplicates(test_user_id):
    async with Client(mcp) as client:
        await client.call_tool("save_user_preference", {"user_id": test_user_id, "key": "currency", "value": "INR"})
        await client.call_tool("save_user_preference", {"user_id": test_user_id, "key": "currency", "value": "EUR"})

        fetched = await client.call_tool("get_user_preference", {"user_id": test_user_id, "key": "currency"})
        assert fetched.data["value"] == "EUR"


@pytest.mark.asyncio
async def test_save_preference_rejects_unsupported_key(test_user_id):
    async with Client(mcp) as client:
        result = await client.call_tool(
            "save_user_preference", {"user_id": test_user_id, "key": "password", "value": "hunter2"}
        )
        assert result.data["success"] is False
        assert "not a supported preference" in result.data["error"]


@pytest.mark.asyncio
async def test_save_preference_rejects_empty_value(test_user_id):
    async with Client(mcp) as client:
        result = await client.call_tool(
            "save_user_preference", {"user_id": test_user_id, "key": "currency", "value": "   "}
        )
        assert result.data["success"] is False


@pytest.mark.asyncio
async def test_get_preference_not_found(test_user_id):
    async with Client(mcp) as client:
        result = await client.call_tool("get_user_preference", {"user_id": test_user_id, "key": "timezone"})
        assert result.data["success"] is True
        assert result.data["found"] is False
        assert result.data["value"] is None


@pytest.mark.asyncio
async def test_save_and_retrieve_context(test_user_id):
    async with Client(mcp) as client:
        await client.call_tool(
            "save_user_context",
            {"user_id": test_user_id, "summary": "User usually reviews weekly spending on Monday mornings."},
        )
        result = await client.call_tool("retrieve_relevant_context", {"user_id": test_user_id})
        assert result.data["success"] is True
        assert result.data["count"] >= 1
        assert "Monday" in result.data["context"][0]["summary"]


@pytest.mark.asyncio
async def test_retrieve_context_keyword_search(test_user_id):
    async with Client(mcp) as client:
        await client.call_tool(
            "save_user_context", {"user_id": test_user_id, "summary": "User asked about gym membership costs."}
        )
        await client.call_tool(
            "save_user_context", {"user_id": test_user_id, "summary": "User asked about grocery budgeting tips."}
        )

        result = await client.call_tool("retrieve_relevant_context", {"user_id": test_user_id, "query": "gym"})
        assert result.data["success"] is True
        assert all("gym" in c["summary"].lower() for c in result.data["context"])
        assert result.data["count"] == 1


@pytest.mark.asyncio
async def test_save_context_rejects_empty_summary(test_user_id):
    async with Client(mcp) as client:
        result = await client.call_tool("save_user_context", {"user_id": test_user_id, "summary": ""})
        assert result.data["success"] is False


@pytest.mark.asyncio
async def test_retrieve_context_rejects_bad_limit(test_user_id):
    async with Client(mcp) as client:
        result = await client.call_tool("retrieve_relevant_context", {"user_id": test_user_id, "limit": 100})
        assert result.data["success"] is False
