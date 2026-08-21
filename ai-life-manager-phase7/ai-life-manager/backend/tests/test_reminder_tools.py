"""Tests for the reminder MCP tools, run through FastMCP's in-memory Client."""

from datetime import date, timedelta

import pytest
from fastmcp import Client

from app.mcp.server import mcp

import app.mcp.prompts  # noqa: F401,E402
import app.mcp.resources  # noqa: F401,E402
import app.mcp.tools  # noqa: F401,E402


@pytest.mark.asyncio
async def test_create_reminder_success(test_user_id):
    async with Client(mcp) as client:
        result = await client.call_tool(
            "create_reminder",
            {"user_id": test_user_id, "title": "Submit assignment", "due_date": "2026-12-31", "due_time": "18:00"},
        )
        assert result.data["success"] is True
        assert result.data["reminder"]["title"] == "Submit assignment"
        assert result.data["reminder"]["status"] == "pending"


@pytest.mark.asyncio
async def test_create_reminder_rejects_empty_title(test_user_id):
    async with Client(mcp) as client:
        result = await client.call_tool(
            "create_reminder", {"user_id": test_user_id, "title": "   ", "due_date": "2026-12-31"}
        )
        assert result.data["success"] is False


@pytest.mark.asyncio
async def test_create_reminder_rejects_invalid_time(test_user_id):
    async with Client(mcp) as client:
        result = await client.call_tool(
            "create_reminder",
            {"user_id": test_user_id, "title": "Test", "due_date": "2026-12-31", "due_time": "not-a-time"},
        )
        assert result.data["success"] is False
        assert "Invalid time" in result.data["error"]


@pytest.mark.asyncio
async def test_list_reminders_today(test_user_id):
    today = date.today().isoformat()
    async with Client(mcp) as client:
        await client.call_tool("create_reminder", {"user_id": test_user_id, "title": "Due today", "due_date": today})
        result = await client.call_tool("list_reminders", {"user_id": test_user_id, "when": "today"})
        assert result.data["success"] is True
        assert any(r["title"] == "Due today" for r in result.data["reminders"])


@pytest.mark.asyncio
async def test_list_reminders_overdue(test_user_id):
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    async with Client(mcp) as client:
        await client.call_tool(
            "create_reminder", {"user_id": test_user_id, "title": "Overdue item", "due_date": yesterday}
        )
        result = await client.call_tool("list_reminders", {"user_id": test_user_id, "when": "overdue"})
        assert result.data["success"] is True
        titles = [r["title"] for r in result.data["reminders"]]
        assert "Overdue item" in titles
        overdue_item = next(r for r in result.data["reminders"] if r["title"] == "Overdue item")
        assert overdue_item["is_overdue"] is True


@pytest.mark.asyncio
async def test_list_reminders_invalid_when(test_user_id):
    async with Client(mcp) as client:
        result = await client.call_tool("list_reminders", {"user_id": test_user_id, "when": "nonsense"})
        assert result.data["success"] is False


@pytest.mark.asyncio
async def test_update_reminder(test_user_id):
    async with Client(mcp) as client:
        created = await client.call_tool(
            "create_reminder", {"user_id": test_user_id, "title": "Original", "due_date": "2026-12-31"}
        )
        reminder_id = created.data["reminder"]["id"]

        updated = await client.call_tool(
            "update_reminder", {"user_id": test_user_id, "reminder_id": reminder_id, "title": "Renamed", "priority": "high"}
        )
        assert updated.data["success"] is True
        assert updated.data["reminder"]["title"] == "Renamed"
        assert updated.data["reminder"]["priority"] == "high"


@pytest.mark.asyncio
async def test_complete_non_recurring_reminder(test_user_id):
    async with Client(mcp) as client:
        created = await client.call_tool(
            "create_reminder", {"user_id": test_user_id, "title": "One-off task", "due_date": "2026-12-31"}
        )
        reminder_id = created.data["reminder"]["id"]

        completed = await client.call_tool("complete_reminder", {"user_id": test_user_id, "reminder_id": reminder_id})
        assert completed.data["success"] is True
        assert completed.data["completed"]["status"] == "completed"
        assert completed.data["next_occurrence"] is None


@pytest.mark.asyncio
async def test_complete_recurring_reminder_creates_next_occurrence(test_user_id):
    async with Client(mcp) as client:
        created = await client.call_tool(
            "create_reminder",
            {
                "user_id": test_user_id,
                "title": "Pay rent",
                "due_date": "2026-01-31",
                "recurrence": "monthly",
            },
        )
        reminder_id = created.data["reminder"]["id"]

        completed = await client.call_tool("complete_reminder", {"user_id": test_user_id, "reminder_id": reminder_id})
        assert completed.data["success"] is True
        assert completed.data["completed"]["status"] == "completed"
        next_occurrence = completed.data["next_occurrence"]
        assert next_occurrence is not None
        assert next_occurrence["status"] == "pending"
        # Jan 31 + 1 month should clamp to Feb 28 (2026 is not a leap year), not overflow into March.
        assert next_occurrence["due_date"] == "2026-02-28"


@pytest.mark.asyncio
async def test_complete_nonexistent_reminder_returns_error(test_user_id):
    async with Client(mcp) as client:
        result = await client.call_tool("complete_reminder", {"user_id": test_user_id, "reminder_id": 9_999_999})
        assert result.data["success"] is False


@pytest.mark.asyncio
async def test_delete_reminder(test_user_id):
    async with Client(mcp) as client:
        created = await client.call_tool(
            "create_reminder", {"user_id": test_user_id, "title": "To delete", "due_date": "2026-12-31"}
        )
        reminder_id = created.data["reminder"]["id"]

        deleted = await client.call_tool("delete_reminder", {"user_id": test_user_id, "reminder_id": reminder_id})
        assert deleted.data["success"] is True

        again = await client.call_tool("delete_reminder", {"user_id": test_user_id, "reminder_id": reminder_id})
        assert again.data["success"] is False
