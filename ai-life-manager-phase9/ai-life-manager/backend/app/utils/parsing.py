"""
Small parsing helpers for turning LLM-supplied strings into typed
values, with clear error messages on failure. Centralized here so
every tool module raises the same style of error for the same kind
of bad input.
"""

from datetime import date, time

from app.models.enums import BudgetPeriod, PaymentMethod, RecurrenceType, ReminderPriority, ReminderStatus


def parse_iso_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise ValueError(f"Invalid date '{value}'. Please use YYYY-MM-DD format.") from None


def parse_time_of_day(value: str) -> time:
    try:
        return time.fromisoformat(value)
    except ValueError:
        raise ValueError(f"Invalid time '{value}'. Please use HH:MM (24-hour) format, e.g. '18:00'.") from None


def parse_payment_method(value: str) -> PaymentMethod:
    try:
        return PaymentMethod(value.strip().lower())
    except ValueError:
        valid = ", ".join(m.value for m in PaymentMethod)
        raise ValueError(f"Invalid payment method '{value}'. Valid options: {valid}") from None


def parse_priority(value: str) -> ReminderPriority:
    try:
        return ReminderPriority(value.strip().lower())
    except ValueError:
        valid = ", ".join(p.value for p in ReminderPriority)
        raise ValueError(f"Invalid priority '{value}'. Valid options: {valid}") from None


def parse_recurrence(value: str) -> RecurrenceType:
    try:
        return RecurrenceType(value.strip().lower())
    except ValueError:
        valid = ", ".join(r.value for r in RecurrenceType)
        raise ValueError(f"Invalid recurrence '{value}'. Valid options: {valid}") from None


def parse_reminder_status(value: str) -> ReminderStatus:
    try:
        return ReminderStatus(value.strip().lower())
    except ValueError:
        valid = ", ".join(s.value for s in ReminderStatus)
        raise ValueError(f"Invalid status '{value}'. Valid options: {valid}") from None


def parse_budget_period(value: str) -> BudgetPeriod:
    try:
        return BudgetPeriod(value.strip().lower())
    except ValueError:
        valid = ", ".join(p.value for p in BudgetPeriod)
        raise ValueError(f"Invalid budget period '{value}'. Valid options: {valid}") from None
