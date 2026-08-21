"""Tests for the analytics MCP tools, run through FastMCP's in-memory Client."""

import pytest
from fastmcp import Client

from app.mcp.server import mcp

import app.mcp.prompts  # noqa: F401,E402
import app.mcp.resources  # noqa: F401,E402
import app.mcp.tools  # noqa: F401,E402


@pytest.mark.asyncio
async def test_calculate_weekly_total_zero_for_fresh_user(test_user_id):
    async with Client(mcp) as client:
        result = await client.call_tool("calculate_weekly_total", {"user_id": test_user_id})
        assert result.data["success"] is True
        assert result.data["total"] == 0.0


@pytest.mark.asyncio
async def test_calculate_weekly_total_reflects_added_expense(test_user_id):
    async with Client(mcp) as client:
        await client.call_tool("add_expense", {"user_id": test_user_id, "amount": 300, "category": "Food"})
        result = await client.call_tool("calculate_weekly_total", {"user_id": test_user_id})
        assert result.data["total"] >= 300.0


@pytest.mark.asyncio
async def test_calculate_percentage_change_basic():
    async with Client(mcp) as client:
        result = await client.call_tool(
            "calculate_percentage_change", {"current_amount": 150, "previous_amount": 100}
        )
        assert result.data["success"] is True
        assert result.data["percentage_change"] == 50.0
        assert result.data["direction"] == "increase"


@pytest.mark.asyncio
async def test_calculate_percentage_change_zero_previous_is_undefined():
    async with Client(mcp) as client:
        result = await client.call_tool(
            "calculate_percentage_change", {"current_amount": 100, "previous_amount": 0}
        )
        assert result.data["percentage_change"] is None
        assert result.data["direction"] is None
        assert "undefined" in result.data["note"]


@pytest.mark.asyncio
async def test_calculate_percentage_change_decrease():
    async with Client(mcp) as client:
        result = await client.call_tool(
            "calculate_percentage_change", {"current_amount": 50, "previous_amount": 100}
        )
        assert result.data["percentage_change"] == -50.0
        assert result.data["direction"] == "decrease"


@pytest.mark.asyncio
async def test_detect_spending_trend_shape(test_user_id):
    async with Client(mcp) as client:
        await client.call_tool("add_expense", {"user_id": test_user_id, "amount": 100, "category": "Food"})
        result = await client.call_tool("detect_spending_trend", {"user_id": test_user_id, "weeks": 3})
        assert result.data["success"] is True
        assert len(result.data["weekly_totals"]) == 3
        assert len(result.data["week_over_week_changes"]) == 2
        assert result.data["trend"] in {"increasing", "decreasing", "stable"}


@pytest.mark.asyncio
async def test_detect_spending_trend_rejects_invalid_weeks(test_user_id):
    async with Client(mcp) as client:
        result = await client.call_tool("detect_spending_trend", {"user_id": test_user_id, "weeks": 1})
        assert result.data["success"] is False


@pytest.mark.asyncio
async def test_detect_unusual_expense_flags_outlier(test_user_id):
    async with Client(mcp) as client:
        # Establish a normal pattern: several small, similar Food expenses.
        for amount in (100, 110, 90, 105):
            await client.call_tool("add_expense", {"user_id": test_user_id, "amount": amount, "category": "Food"})
        # Now a clear outlier in the same category.
        big = await client.call_tool("add_expense", {"user_id": test_user_id, "amount": 5000, "category": "Food"})
        big_id = big.data["expense"]["id"]

        result = await client.call_tool(
            "detect_unusual_expense", {"user_id": test_user_id, "threshold_multiplier": 2.5}
        )
        assert result.data["success"] is True
        flagged_ids = [e["expense_id"] for e in result.data["unusual_expenses"]]
        assert big_id in flagged_ids


@pytest.mark.asyncio
async def test_detect_unusual_expense_no_history_no_flags(test_user_id):
    async with Client(mcp) as client:
        # Only one expense ever in this category — not enough history to judge.
        await client.call_tool("add_expense", {"user_id": test_user_id, "amount": 99999, "category": "Travel"})
        result = await client.call_tool("detect_unusual_expense", {"user_id": test_user_id})
        assert result.data["success"] is True
        assert result.data["count"] == 0


@pytest.mark.asyncio
async def test_detect_unusual_expense_rejects_bad_threshold(test_user_id):
    async with Client(mcp) as client:
        result = await client.call_tool(
            "detect_unusual_expense", {"user_id": test_user_id, "threshold_multiplier": 0.5}
        )
        assert result.data["success"] is False


@pytest.mark.asyncio
async def test_generate_financial_insight_shape(test_user_id):
    async with Client(mcp) as client:
        await client.call_tool("add_expense", {"user_id": test_user_id, "amount": 200, "category": "Food"})
        result = await client.call_tool("generate_financial_insight", {"user_id": test_user_id})
        assert result.data["success"] is True
        assert "insight_text" in result.data
        assert "disclaimer" in result.data
        assert isinstance(result.data["insight_text"], str) and len(result.data["insight_text"]) > 0
