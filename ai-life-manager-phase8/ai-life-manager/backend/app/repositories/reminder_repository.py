"""Repository for the reminders table."""

from datetime import date, datetime, time, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import RecurrenceType, ReminderPriority, ReminderStatus
from app.models.reminder import Reminder


async def create_reminder(
    session: AsyncSession,
    *,
    user_id: int,
    title: str,
    description: str | None,
    due_date: date,
    due_time: time | None,
    priority: ReminderPriority,
    recurrence: RecurrenceType,
) -> Reminder:
    reminder = Reminder(
        user_id=user_id,
        title=title,
        description=description,
        due_date=due_date,
        due_time=due_time,
        priority=priority,
        recurrence=recurrence,
        status=ReminderStatus.PENDING,
    )
    session.add(reminder)
    await session.commit()
    await session.refresh(reminder)
    return reminder


async def get_reminder(session: AsyncSession, user_id: int, reminder_id: int) -> Reminder | None:
    stmt = select(Reminder).where(Reminder.id == reminder_id, Reminder.user_id == user_id)
    result = await session.execute(stmt)
    return result.scalars().first()


async def list_reminders(
    session: AsyncSession,
    user_id: int,
    *,
    status: ReminderStatus | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    limit: int = 50,
) -> list[Reminder]:
    stmt = select(Reminder).where(Reminder.user_id == user_id)
    if status is not None:
        stmt = stmt.where(Reminder.status == status)
    if start_date is not None:
        stmt = stmt.where(Reminder.due_date >= start_date)
    if end_date is not None:
        stmt = stmt.where(Reminder.due_date <= end_date)
    stmt = stmt.order_by(Reminder.due_date.asc(), Reminder.due_time.asc()).limit(limit)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def update_reminder(session: AsyncSession, user_id: int, reminder_id: int, **fields) -> Reminder | None:
    reminder = await get_reminder(session, user_id, reminder_id)
    if reminder is None:
        return None
    for key, value in fields.items():
        if value is not None:
            setattr(reminder, key, value)
    await session.commit()
    await session.refresh(reminder)
    return reminder


async def mark_completed(session: AsyncSession, user_id: int, reminder_id: int) -> Reminder | None:
    reminder = await get_reminder(session, user_id, reminder_id)
    if reminder is None:
        return None
    reminder.status = ReminderStatus.COMPLETED
    reminder.completed_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(reminder)
    return reminder


async def delete_reminder(session: AsyncSession, user_id: int, reminder_id: int) -> bool:
    reminder = await get_reminder(session, user_id, reminder_id)
    if reminder is None:
        return False
    await session.delete(reminder)
    await session.commit()
    return True
