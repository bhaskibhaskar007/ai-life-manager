"""
Small parsing helpers for turning LLM-supplied strings into typed
values, with clear error messages on failure. Centralized here so
every tool module raises the same style of error for the same kind
of bad input.
"""

from datetime import date

from app.models.enums import PaymentMethod


def parse_iso_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise ValueError(f"Invalid date '{value}'. Please use YYYY-MM-DD format.") from None


def parse_payment_method(value: str) -> PaymentMethod:
    try:
        return PaymentMethod(value.strip().lower())
    except ValueError:
        valid = ", ".join(m.value for m in PaymentMethod)
        raise ValueError(f"Invalid payment method '{value}'. Valid options: {valid}") from None
