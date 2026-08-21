"""
Safe, explicit calculation helpers.

Per project requirements: NEVER use eval() for any numeric calculation.
Every formula the app needs (percentage change, averages, etc.) is a
plain typed Python function here, reused by both expense tools and the
analytics tools built in Phase 5 — so there is exactly one
implementation of "percentage change" in the whole codebase.
"""

from decimal import Decimal


def safe_percentage_change(current: Decimal, previous: Decimal) -> float | None:
    """
    ((current - previous) / previous) * 100

    Returns None when `previous` is 0 — percentage change is undefined
    there, not infinite. Callers should render this as something like
    "no prior spending to compare against" rather than a number.
    """
    if previous == 0:
        return None
    return float((current - previous) / previous * 100)


def safe_average(total: Decimal, count: int) -> float:
    """Average with an explicit zero-count guard instead of a raw ZeroDivisionError."""
    if count == 0:
        return 0.0
    return float(total / count)


def round_currency(value: Decimal | float) -> float:
    """Round to 2 decimal places for currency display, always as float for JSON output."""
    return round(float(value), 2)
