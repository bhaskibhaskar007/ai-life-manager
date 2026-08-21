"""
Reminder MCP tools.

`when` convenience filters (today/tomorrow/upcoming/overdue) exist so
the LLM doesn't need to compute date arithmetic itself for common
questions like "what's due today" or "what's overdue" — it just picks
the matching value.
"""

from app.database import AsyncSessionLocal
from app.mcp.logging import log_tool_execution
from app.mcp.server import mcp
from app.models.enums import RecurrenceType, ReminderPriority
from app.services.reminder_service import ReminderService
from app.utils.parsing import parse_iso_date, parse_priority, parse_recurrence, parse_reminder_status, parse_time_of_day


@mcp.tool
@log_tool_execution("create_reminder")
async def create_reminder(
    user_id: int,
    title: str,
    due_date: str,
    description: str | None = None,
    due_time: str | None = None,
    priority: str = "medium",
    recurrence: str = "none",
) -> dict:
    """
    Create a reminder. `due_date` must be YYYY-MM-DD — resolve relative
    phrases like "tomorrow" or "next Friday" to an actual date yourself
    before calling this tool, using the current date for reference.
    `due_time` (optional) is HH:MM 24-hour format. `priority` is one
    of: low, medium, high. `recurrence` is one of: none, daily, weekly,
    monthly.
    """
    async with AsyncSessionLocal() as session:
        service = ReminderService(session)
        result = await service.create_reminder(
            user_id=user_id,
            title=title,
            due_date=parse_iso_date(due_date),
            description=description,
            due_time=parse_time_of_day(due_time) if due_time else None,
            priority=parse_priority(priority),
            recurrence=parse_recurrence(recurrence),
        )
        return {"success": True, "reminder": result}


@mcp.tool
@log_tool_execution("list_reminders")
async def list_reminders(
    user_id: int,
    when: str = "all",
    status: str | None = None,
    limit: int = 50,
) -> dict:
    """
    List the user's reminders. `when` is one of: all, today, tomorrow,
    upcoming (today onward), overdue (past due and still pending).
    `status` optionally filters further: pending, completed, overdue,
    cancelled. Each reminder includes `is_overdue` computed live from
    today's date, so you don't need to compute that yourself.
    """
    async with AsyncSessionLocal() as session:
        service = ReminderService(session)
        reminders = await service.list_reminders(
            user_id=user_id,
            when=when,
            status=parse_reminder_status(status) if status else None,
            limit=limit,
        )
        return {"success": True, "count": len(reminders), "reminders": reminders}


@mcp.tool
@log_tool_execution("update_reminder")
async def update_reminder(
    user_id: int,
    reminder_id: int,
    title: str | None = None,
    description: str | None = None,
    due_date: str | None = None,
    due_time: str | None = None,
    priority: str | None = None,
    recurrence: str | None = None,
) -> dict:
    """Update one or more fields of an existing reminder. Only fields you provide are changed."""
    async with AsyncSessionLocal() as session:
        service = ReminderService(session)
        result = await service.update_reminder(
            user_id=user_id,
            reminder_id=reminder_id,
            title=title,
            description=description,
            due_date=parse_iso_date(due_date) if due_date else None,
            due_time=parse_time_of_day(due_time) if due_time else None,
            priority=parse_priority(priority) if priority else None,
            recurrence=parse_recurrence(recurrence) if recurrence else None,
        )
        if result is None:
            return {"success": False, "error": f"No reminder with id {reminder_id} found for this user."}
        return {"success": True, "reminder": result}


@mcp.tool
@log_tool_execution("complete_reminder")
async def complete_reminder(user_id: int, reminder_id: int) -> dict:
    """
    Mark a reminder as completed. If it was recurring (daily/weekly/
    monthly), the next occurrence is automatically created as a new
    pending reminder — returned as `next_occurrence`.
    """
    async with AsyncSessionLocal() as session:
        service = ReminderService(session)
        result = await service.complete_reminder(user_id=user_id, reminder_id=reminder_id)
        if result is None:
            return {"success": False, "error": f"No reminder with id {reminder_id} found for this user."}
        return {"success": True, **result}


@mcp.tool
@log_tool_execution("delete_reminder")
async def delete_reminder(user_id: int, reminder_id: int) -> dict:
    """Permanently delete a reminder by id."""
    async with AsyncSessionLocal() as session:
        service = ReminderService(session)
        deleted = await service.delete_reminder(user_id=user_id, reminder_id=reminder_id)
        if not deleted:
            return {"success": False, "error": f"No reminder with id {reminder_id} found for this user."}
        return {"success": True, "deleted_reminder_id": reminder_id}
