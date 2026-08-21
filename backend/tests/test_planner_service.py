"""
Tests for Day Planner service and MCP tool.
"""

from datetime import date, time, timedelta
import pytest
from fastmcp import Client

from app.mcp.server import mcp
from app.models.enums import ReminderPriority, ReminderStatus
from app.services.planner_service import PlannerService
from app.services.reminder_service import ReminderService


@pytest.mark.asyncio
async def test_planner_service_generates_day_plan(db_session, test_user_id):
    rem_service = ReminderService(db_session)
    await rem_service.create_reminder(
        user_id=test_user_id,
        title="College Assignment Submission",
        due_date=date.today(),
        due_time=time(18, 0),
        priority=ReminderPriority.HIGH,
    )
    await rem_service.create_reminder(
        user_id=test_user_id,
        title="Morning Gym",
        due_date=date.today(),
        due_time=time(7, 30),
        priority=ReminderPriority.MEDIUM,
    )

    planner = PlannerService(db_session)
    plan = await planner.generate_day_plan(user_id=test_user_id, target_date=date.today(), location="Bengaluru")

    assert plan["date"] == date.today().isoformat()
    assert plan["reminders_count"] >= 2
    assert len(plan["schedule_blocks"]) == 3
    assert len(plan["timed_reminders"]) >= 2
    # Verify chronological sorting
    assert plan["timed_reminders"][0]["time"] <= plan["timed_reminders"][1]["time"]


@pytest.mark.asyncio
async def test_plan_day_mcp_tool(test_user_id):
    async with Client(mcp) as client:
        result = await client.call_tool("plan_day", {"user_id": test_user_id, "target_date": date.today().isoformat()})
        assert result.data["success"] is True
        assert "plan" in result.data
        assert result.data["plan"]["date"] == date.today().isoformat()
