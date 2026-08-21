"""
Deterministic fallback intent matching.

Deliberately narrow: this is NOT meant to replace the LLM's intent
understanding - it's a degraded-mode safety net covering only the
most common, unambiguous phrasings, so the assistant still does
something useful if the Anthropic API is unreachable, rate-limited,
or unconfigured (no API key set). Anything it doesn't recognize
returns None and the caller shows a clear "I'm in degraded mode"
message rather than guessing.
"""

import re

_ADD_EXPENSE_RE = re.compile(
    r"(?:spent|paid)\s*(?:rs\.?|Rs\.?|inr)?\s*(\d+(?:\.\d+)?)\s*(?:rs\.?|Rs\.?|inr)?\s*(?:on|for)\s+([a-zA-Z ]+)",
    re.IGNORECASE,
)
_WEEKLY_SUMMARY_RE = re.compile(r"how much.*(spen[dt]).*week|weekly (spending|summary|total)", re.IGNORECASE)
_OVERDUE_REMINDERS_RE = re.compile(r"overdue|what.*reminders", re.IGNORECASE)


def match_intent(message: str) -> dict | None:
    """Returns {"tool": str, "arguments": dict} (without user_id - caller adds that) or None."""
    match = _ADD_EXPENSE_RE.search(message)
    if match:
        amount = float(match.group(1))
        category = match.group(2).strip().rstrip(".").title()
        return {"tool": "add_expense", "arguments": {"amount": amount, "category": category}}

    if _WEEKLY_SUMMARY_RE.search(message):
        return {"tool": "compare_weekly_expenses", "arguments": {}}

    if _OVERDUE_REMINDERS_RE.search(message):
        return {"tool": "list_reminders", "arguments": {"when": "overdue"}}

    return None
