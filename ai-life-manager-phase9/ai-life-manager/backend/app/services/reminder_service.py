"""
Reminder service layer.

Natural-language phrases like "tomorrow at 6 PM" are resolved by the
AI/intent layer (Phase 10) into an explicit YYYY-MM-DD / HH:MM before
ever reaching this service or the MCP tools — this layer only works
with already-structured dates, which keeps it deterministic and
testable independent of any LLM.
"""

import calendar
from datetime import date, time, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import RecurrenceType, ReminderPriority, ReminderStatus
from app.models.reminder import Reminder
from app.repositories import reminder_repository


def _advance_due_date(due_date: date, recurrence: RecurrenceType) -> date | None:
    """Returns the next occurrence's due date for a recurring reminder, or None if not recurring."""
    if recurrence == RecurrenceType.DAILY:
        return due_date + timedelta(days=1)
    if recurrence == RecurrenceType.WEEKLY:
        return due_date + timedelta(weeks=1)
    if recurrence == RecurrenceType.MONTHLY:
        month = due_date.month + 1
        year = due_date.year + (1 if month > 12 else 0)
        month = 1 if month > 12 else month
        # Clamp to the last valid day of the target month (e.g. Jan 31 -> Feb 28/29)
        day = min(due_date.day, calendar.monthrange(year, month)[1])
        return date(year, month, day)
    return None


def _serialize_reminder(reminder: Reminder) -> dict:
    is_overdue = reminder.status == ReminderStatus.PENDING and reminder.due_date < date.today()
    return {
        "id": reminder.id,
        "title": reminder.title,
        "description": reminder.description,
        "due_date": reminder.due_date.isoformat(),
        "due_time": reminder.due_time.isoformat(timespec="minutes") if reminder.due_time else None,
        "priority": reminder.priority.value,
        "status": reminder.status.value,
        "recurrence": reminder.recurrence.value,
        "is_overdue": is_overdue,
    }


class ReminderService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_reminder(
        self,
        *,
        user_id: int,
        title: str,
        due_date: date,
        description: str | None = None,
        due_time: time | None = None,
        priority: ReminderPriority = ReminderPriority.MEDIUM,
        recurrence: RecurrenceType = RecurrenceType.NONE,
    ) -> dict:
        if not title or not title.strip():
            raise ValueError("A reminder title is required.")
        if len(title) > 255:
            raise ValueError("Title is too long (255 characters max).")

        reminder = await reminder_repository.create_reminder(
            self.session,
            user_id=user_id,
            title=title.strip(),
            description=description,
            due_date=due_date,
            due_time=due_time,
            priority=priority,
            recurrence=recurrence,
        )
        return _serialize_reminder(reminder)

    async def list_reminders(
        self,
        *,
        user_id: int,
        when: str = "all",
        status: ReminderStatus | None = None,
        limit: int = 50,
    ) -> list[dict]:
        today = date.today()
        start_date = end_date = None

        if when == "today":
            start_date = end_date = today
        elif when == "tomorrow":
            start_date = end_date = today + timedelta(days=1)
        elif when == "upcoming":
            start_date = today
        elif when == "overdue":
            end_date = today - timedelta(days=1)
            if status is None:
                status = ReminderStatus.PENDING
        elif when != "all":
            raise ValueError("when must be one of: all, today, tomorrow, upcoming, overdue.")

        reminders = await reminder_repository.list_reminders(
            self.session, user_id, status=status, start_date=start_date, end_date=end_date, limit=limit
        )
        return [_serialize_reminder(r) for r in reminders]

    async def update_reminder(
        self,
        *,
        user_id: int,
        reminder_id: int,
        title: str | None = None,
        description: str | None = None,
        due_date: date | None = None,
        due_time: time | None = None,
        priority: ReminderPriority | None = None,
        recurrence: RecurrenceType | None = None,
    ) -> dict | None:
        if title is not None and not title.strip():
            raise ValueError("Title cannot be empty.")

        reminder = await reminder_repository.update_reminder(
            self.session,
            user_id,
            reminder_id,
            title=title.strip() if title else None,
            description=description,
            due_date=due_date,
            due_time=due_time,
            priority=priority,
            recurrence=recurrence,
        )
        if reminder is None:
            return None
        return _serialize_reminder(reminder)

    async def complete_reminder(self, *, user_id: int, reminder_id: int) -> dict | None:
        reminder = await reminder_repository.get_reminder(self.session, user_id, reminder_id)
        if reminder is None:
            return None

        completed = await reminder_repository.mark_completed(self.session, user_id, reminder_id)
        result = {"completed": _serialize_reminder(completed), "next_occurrence": None}

        next_due = _advance_due_date(completed.due_date, completed.recurrence)
        if next_due is not None:
            next_reminder = await reminder_repository.create_reminder(
                self.session,
                user_id=user_id,
                title=completed.title,
                description=completed.description,
                due_date=next_due,
                due_time=completed.due_time,
                priority=completed.priority,
                recurrence=completed.recurrence,
            )
            result["next_occurrence"] = _serialize_reminder(next_reminder)

        return result

    async def delete_reminder(self, *, user_id: int, reminder_id: int) -> bool:
        return await reminder_repository.delete_reminder(self.session, user_id, reminder_id)
