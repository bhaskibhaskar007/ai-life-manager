"""Week-boundary helpers. A "week" is Monday–Sunday throughout the app."""

from datetime import date, timedelta


def get_week_range(reference: date | None = None) -> tuple[date, date]:
    """Returns (Monday, Sunday) of the week containing `reference` (default: today)."""
    ref = reference or date.today()
    start = ref - timedelta(days=ref.weekday())
    end = start + timedelta(days=6)
    return start, end


def get_previous_week_range(reference: date | None = None) -> tuple[date, date]:
    start, _ = get_week_range(reference)
    prev_start = start - timedelta(days=7)
    prev_end = start - timedelta(days=1)
    return prev_start, prev_end


def get_month_range(reference: date | None = None) -> tuple[date, date]:
    ref = reference or date.today()
    start = ref.replace(day=1)
    if ref.month == 12:
        next_month_start = ref.replace(year=ref.year + 1, month=1, day=1)
    else:
        next_month_start = ref.replace(month=ref.month + 1, day=1)
    end = next_month_start - timedelta(days=1)
    return start, end
