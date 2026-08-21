"""Tests for the expense MCP tools, run through FastMCP's in-memory Client."""

import pytest
from fastmcp import Client

from app.mcp.server import mcp

import app.mcp.prompts  # noqa: F401,E402
import app.mcp.resources  # noqa: F401,E402
import app.mcp.tools  # noqa: F401,E402


@pytest.mark.asyncio
async def test_add_expense_success(test_user_id):
    async with Client(mcp) as client:
        result = await client.call_tool(
            "add_expense",
            {"user_id": test_user_id, "amount": 250, "category": "Food", "description": "Lunch"},
        )
        data = result.data
        assert data["success"] is True
        assert data["expense"]["amount"] == 250.0
        assert data["expense"]["category"] == "Food"


@pytest.mark.asyncio
async def test_add_expense_creates_custom_category(test_user_id):
    async with Client(mcp) as client:
        result = await client.call_tool(
            "add_expense",
            {"user_id": test_user_id, "amount": 99, "category": "Pottery Classes"},
        )
        assert result.data["success"] is True
        assert result.data["expense"]["category"] == "Pottery Classes"


@pytest.mark.asyncio
async def test_add_expense_rejects_negative_amount(test_user_id):
    async with Client(mcp) as client:
        result = await client.call_tool(
            "add_expense",
            {"user_id": test_user_id, "amount": -50, "category": "Food"},
        )
        assert result.data["success"] is False
        assert "greater than zero" in result.data["error"]


@pytest.mark.asyncio
async def test_add_expense_rejects_invalid_date(test_user_id):
    async with Client(mcp) as client:
        result = await client.call_tool(
            "add_expense",
            {"user_id": test_user_id, "amount": 50, "category": "Food", "date": "not-a-date"},
        )
        assert result.data["success"] is False
        assert "Invalid date" in result.data["error"]


@pytest.mark.asyncio
async def test_get_expenses_returns_added_expense(test_user_id):
    async with Client(mcp) as client:
        await client.call_tool(
            "add_expense", {"user_id": test_user_id, "amount": 120, "category": "Transportation"}
        )
        result = await client.call_tool("get_expenses", {"user_id": test_user_id})
        assert result.data["success"] is True
        categories = [e["category"] for e in result.data["expenses"]]
        assert "Transportation" in categories


@pytest.mark.asyncio
async def test_get_expenses_unknown_category_returns_empty(test_user_id):
    async with Client(mcp) as client:
        result = await client.call_tool(
            "get_expenses", {"user_id": test_user_id, "category": "Nonexistent Category XYZ"}
        )
        assert result.data["success"] is True
        assert result.data["count"] == 0


@pytest.mark.asyncio
async def test_update_expense(test_user_id):
    async with Client(mcp) as client:
        added = await client.call_tool(
            "add_expense", {"user_id": test_user_id, "amount": 100, "category": "Food"}
        )
        expense_id = added.data["expense"]["id"]

        updated = await client.call_tool(
            "update_expense", {"user_id": test_user_id, "expense_id": expense_id, "amount": 150}
        )
        assert updated.data["success"] is True
        assert updated.data["expense"]["amount"] == 150.0


@pytest.mark.asyncio
async def test_update_nonexistent_expense_returns_error(test_user_id):
    async with Client(mcp) as client:
        result = await client.call_tool(
            "update_expense", {"user_id": test_user_id, "expense_id": 9_999_999, "amount": 10}
        )
        assert result.data["success"] is False


@pytest.mark.asyncio
async def test_delete_expense(test_user_id):
    async with Client(mcp) as client:
        added = await client.call_tool(
            "add_expense", {"user_id": test_user_id, "amount": 75, "category": "Shopping"}
        )
        expense_id = added.data["expense"]["id"]

        deleted = await client.call_tool("delete_expense", {"user_id": test_user_id, "expense_id": expense_id})
        assert deleted.data["success"] is True

        again = await client.call_tool("delete_expense", {"user_id": test_user_id, "expense_id": expense_id})
        assert again.data["success"] is False


@pytest.mark.asyncio
async def test_expense_summary(test_user_id):
    async with Client(mcp) as client:
        await client.call_tool("add_expense", {"user_id": test_user_id, "amount": 200, "category": "Food"})
        await client.call_tool("add_expense", {"user_id": test_user_id, "amount": 300, "category": "Bills"})

        result = await client.call_tool("get_expense_summary", {"user_id": test_user_id})
        assert result.data["success"] is True
        assert result.data["summary"]["total"] >= 500.0
        assert result.data["summary"]["transaction_count"] >= 2


@pytest.mark.asyncio
async def test_category_breakdown(test_user_id):
    async with Client(mcp) as client:
        await client.call_tool("add_expense", {"user_id": test_user_id, "amount": 400, "category": "Food"})

        result = await client.call_tool("get_category_breakdown", {"user_id": test_user_id})
        assert result.data["success"] is True
        assert result.data["top_category"] is not None
        assert any(row["category"] == "Food" for row in result.data["breakdown"])


@pytest.mark.asyncio
async def test_compare_weekly_expenses(test_user_id):
    async with Client(mcp) as client:
        await client.call_tool("add_expense", {"user_id": test_user_id, "amount": 100, "category": "Food"})

        result = await client.call_tool("compare_weekly_expenses", {"user_id": test_user_id})
        assert result.data["success"] is True
        assert "current_week" in result.data
        assert "previous_week" in result.data
        # No prior-week expenses were seeded for this fresh user, so
        # change_percent should be None (undefined), not a crash.
        assert result.data["change_percent"] is None
        assert result.data["note"] is not None


@pytest.mark.asyncio
async def test_spending_trend(test_user_id):
    async with Client(mcp) as client:
        await client.call_tool("add_expense", {"user_id": test_user_id, "amount": 50, "category": "Food"})

        result = await client.call_tool("get_spending_trend", {"user_id": test_user_id, "weeks": 3})
        assert result.data["success"] is True
        assert len(result.data["weeks"]) == 3
        assert result.data["trend"] in {"increasing", "decreasing", "stable"}


@pytest.mark.asyncio
async def test_spending_trend_rejects_out_of_range_weeks(test_user_id):
    async with Client(mcp) as client:
        result = await client.call_tool("get_spending_trend", {"user_id": test_user_id, "weeks": 1})
        assert result.data["success"] is False
