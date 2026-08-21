"""Tests for the budget MCP tools, run through FastMCP's in-memory Client."""

import pytest
from fastmcp import Client

from app.mcp.server import mcp

import app.mcp.prompts  # noqa: F401,E402
import app.mcp.resources  # noqa: F401,E402
import app.mcp.tools  # noqa: F401,E402


@pytest.mark.asyncio
async def test_create_and_get_overall_budget(test_user_id):
    async with Client(mcp) as client:
        created = await client.call_tool(
            "create_budget", {"user_id": test_user_id, "amount": 10000, "period": "monthly"}
        )
        assert created.data["success"] is True
        assert created.data["budget"]["category"] is None
        assert created.data["budget"]["was_updated"] is False

        fetched = await client.call_tool("get_budget", {"user_id": test_user_id})
        assert fetched.data["success"] is True
        assert fetched.data["budget"]["amount"] == 10000.0


@pytest.mark.asyncio
async def test_create_budget_upserts_existing(test_user_id):
    async with Client(mcp) as client:
        await client.call_tool("create_budget", {"user_id": test_user_id, "amount": 5000, "category": "Food"})
        second = await client.call_tool(
            "create_budget", {"user_id": test_user_id, "amount": 7000, "category": "Food"}
        )
        assert second.data["budget"]["was_updated"] is True
        assert second.data["budget"]["amount"] == 7000.0

        fetched = await client.call_tool("get_budget", {"user_id": test_user_id, "category": "Food"})
        assert fetched.data["budget"]["amount"] == 7000.0


@pytest.mark.asyncio
async def test_get_budget_not_found(test_user_id):
    async with Client(mcp) as client:
        result = await client.call_tool("get_budget", {"user_id": test_user_id, "category": "Travel"})
        assert result.data["success"] is False


@pytest.mark.asyncio
async def test_create_budget_rejects_invalid_amount(test_user_id):
    async with Client(mcp) as client:
        result = await client.call_tool("create_budget", {"user_id": test_user_id, "amount": -100})
        assert result.data["success"] is False


@pytest.mark.asyncio
async def test_create_budget_rejects_invalid_period(test_user_id):
    async with Client(mcp) as client:
        result = await client.call_tool(
            "create_budget", {"user_id": test_user_id, "amount": 1000, "period": "fortnightly"}
        )
        assert result.data["success"] is False


@pytest.mark.asyncio
async def test_calculate_remaining_budget(test_user_id):
    async with Client(mcp) as client:
        await client.call_tool("create_budget", {"user_id": test_user_id, "amount": 1000, "category": "Food"})
        await client.call_tool("add_expense", {"user_id": test_user_id, "amount": 300, "category": "Food"})

        result = await client.call_tool("calculate_remaining_budget", {"user_id": test_user_id, "category": "Food"})
        assert result.data["success"] is True
        assert result.data["spent"] == 300.0
        assert result.data["remaining"] == 700.0
        assert result.data["percentage_used"] == 30.0
        assert result.data["status"] == "on_track"


@pytest.mark.asyncio
async def test_calculate_remaining_budget_no_budget_set(test_user_id):
    async with Client(mcp) as client:
        result = await client.call_tool(
            "calculate_remaining_budget", {"user_id": test_user_id, "category": "Entertainment"}
        )
        assert result.data["success"] is False
        assert "No budget" in result.data["error"]


@pytest.mark.asyncio
async def test_detect_budget_risk_flags_high_usage(test_user_id):
    async with Client(mcp) as client:
        await client.call_tool("create_budget", {"user_id": test_user_id, "amount": 1000, "category": "Shopping"})
        await client.call_tool("add_expense", {"user_id": test_user_id, "amount": 900, "category": "Shopping"})

        result = await client.call_tool("detect_budget_risk", {"user_id": test_user_id, "threshold_percent": 80})
        assert result.data["success"] is True
        assert result.data["at_risk_count"] >= 1
        shopping_budget = next(b for b in result.data["budgets"] if b["category"] == "Shopping")
        assert shopping_budget["status"] in {"at_risk", "exceeded"}


@pytest.mark.asyncio
async def test_detect_budget_risk_rejects_bad_threshold(test_user_id):
    async with Client(mcp) as client:
        result = await client.call_tool("detect_budget_risk", {"user_id": test_user_id, "threshold_percent": 150})
        assert result.data["success"] is False
