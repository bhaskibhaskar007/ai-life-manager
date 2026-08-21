"""Reminder model."""

import datetime as dt

from sqlalchemy import Date, DateTime, ForeignKey, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import RecurrenceType, ReminderPriority, ReminderStatus


class Reminder(Base):
    __tablename__ = "reminders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    due_date: Mapped[dt.date] = mapped_column(Date, nullable=False, index=True)
    due_time: Mapped[dt.time | None] = mapped_column(Time, nullable=True)
    priority: Mapped[ReminderPriority] = mapped_column(
        default=ReminderPriority.MEDIUM, server_default=ReminderPriority.MEDIUM.value
    )
    status: Mapped[ReminderStatus] = mapped_column(
        default=ReminderStatus.PENDING, server_default=ReminderStatus.PENDING.value, index=True
    )
    recurrence: Mapped[RecurrenceType] = mapped_column(
        default=RecurrenceType.NONE, server_default=RecurrenceType.NONE.value
    )

    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: dt.datetime.now(dt.timezone.utc)
    )
    completed_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship(back_populates="reminders")

    def __repr__(self) -> str:
        return f"<Reminder id={self.id} title={self.title!r} status={self.status}>"
