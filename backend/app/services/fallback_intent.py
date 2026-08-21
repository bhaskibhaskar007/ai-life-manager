"""
Deterministic fallback intent matching.

Deliberately robust and structured: covers the primary user command
patterns so that the assistant operates effectively even when the
primary LLM is offline, rate-limited, or running without an API key.

When the LLM is available, it handles more complex conversational nuances,
while this fallback handles standard productivity and financial phrases.
"""

from datetime import date, datetime, timedelta
import re

# Regex patterns for various natural language intents
_ADD_EXPENSE_RE = re.compile(
    r"(?:spent|paid|add|bought|purchased)\s*(?:rs\.?|Rs\.?|inr|₹|\$)?\s*(\d+(?:\.\d+)?)\s*(?:rs\.?|Rs\.?|inr|₹|\$)?\s*(?:on|for|towards)\s+([a-zA-Z\s]+?)(?:\s+(?:today|yesterday|with\s+card|via\s+upi|in\s+cash))?$",
    re.IGNORECASE,
)
_ADD_EXPENSE_ALT_RE = re.compile(
    r"(?:add|record|track)\s*(?:an?\s+)?(?:expense\s+of\s+)?(?:rs\.?|Rs\.?|inr|₹|\$)?\s*(\d+(?:\.\d+)?)\s*(?:for|on|under)\s+([a-zA-Z\s]+)",
    re.IGNORECASE,
)

_WEEKLY_COMPARE_RE = re.compile(
    r"(?:compare.*spending.*last week|how much.*(?:spen[dt]).*week|weekly (?:spending|summary|total|comparison))",
    re.IGNORECASE,
)

_CATEGORY_BREAKDOWN_RE = re.compile(
    r"(?:which category.*spend.*most|top spending category|category breakdown|where is my money going|spending by category)",
    re.IGNORECASE,
)

_FINANCIAL_INSIGHTS_RE = re.compile(
    r"(?:why did my expenses increase|summary of my financial habits|financial (?:insights?|habits|summary)|spending habits)",
    re.IGNORECASE,
)

_SAFE_SPEND_RE = re.compile(
    r"(?:safely spend|remaining budget|budget status|how much can i.*spend|budget remaining)",
    re.IGNORECASE,
)

_WEATHER_RE = re.compile(
    r"(?:do i need an umbrella|umbrella today|weather(?: in| for)?\s*([a-zA-Z\s]+)?|will it rain|is it raining)",
    re.IGNORECASE,
)

_PLAN_DAY_RE = re.compile(
    r"(?:plan my day|daily plan|schedule my day|what's my schedule|what is on my schedule today)",
    re.IGNORECASE,
)

_CREATE_REMINDER_RE = re.compile(
    r"remind me to\s+(.+?)(?:\s+(tomorrow|today|on\s+[a-zA-Z0-9\s]+))?(?:\s+at\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm)?))?$",
    re.IGNORECASE,
)

_LIST_REMINDERS_RE = re.compile(
    r"(?:show|list|get|what are)\s*(?:my\s*)?(pending|overdue|upcoming|today's)?\s*reminders",
    re.IGNORECASE,
)


def match_intent(message: str) -> dict | None:
    """
    Analyzes message and returns dict with tool name and structured arguments,
    or None if no deterministic match is found.
    """
    clean_msg = message.strip()

    # 1. Add Expense
    match = _ADD_EXPENSE_RE.search(clean_msg) or _ADD_EXPENSE_ALT_RE.search(clean_msg)
    if match:
        try:
            amount = float(match.group(1))
            category_raw = match.group(2).strip().rstrip(".").title()
            # Clean common trailing prepositions/words
            for word in ["Today", "Yesterday", "Via Upi", "In Cash", "With Card"]:
                if category_raw.endswith(word):
                    category_raw = category_raw[: -len(word)].strip()
            return {
                "tool": "add_expense",
                "arguments": {
                    "amount": amount,
                    "category": category_raw or "Other",
                    "description": f"Expense on {category_raw or 'Other'}",
                },
            }
        except (ValueError, IndexError):
            pass

    # 2. Day Planning
    if _PLAN_DAY_RE.search(clean_msg):
        return {"tool": "plan_day", "arguments": {"target_date": date.today().isoformat()}}

    # 3. Weather / Umbrella
    w_match = _WEATHER_RE.search(clean_msg)
    if w_match:
        loc = w_match.group(1).strip() if (w_match.lastindex and w_match.group(1)) else "Bengaluru"
        return {"tool": "get_current_weather", "arguments": {"location": loc}}

    # 4. Safe Spending / Budget
    if _SAFE_SPEND_RE.search(clean_msg):
        return {"tool": "calculate_remaining_budget", "arguments": {}}

    # 5. Financial Habits / Insights
    if _FINANCIAL_INSIGHTS_RE.search(clean_msg):
        return {"tool": "generate_financial_insight", "arguments": {}}

    # 6. Category Breakdown
    if _CATEGORY_BREAKDOWN_RE.search(clean_msg):
        return {"tool": "get_category_breakdown", "arguments": {}}

    # 7. Weekly Spending & Comparison
    if _WEEKLY_COMPARE_RE.search(clean_msg):
        return {"tool": "compare_weekly_expenses", "arguments": {}}

    # 8. Create Reminder
    rem_match = _CREATE_REMINDER_RE.search(clean_msg)
    if rem_match:
        title = rem_match.group(1).strip()
        when_str = (rem_match.group(2) or "today").strip().lower()
        time_str = rem_match.group(3)

        due_date = date.today()
        if "tomorrow" in when_str:
            due_date = date.today() + timedelta(days=1)

        formatted_time = None
        if time_str:
            t = time_str.strip().lower()
            # Parse simple times e.g. 6 pm, 6:30 pm, 18:00
            try:
                if "pm" in t or "am" in t:
                    parsed_t = datetime.strptime(t.replace(" ", ""), "%I:%M%p" if ":" in t else "%I%p").time()
                    formatted_time = parsed_t.strftime("%H:%M")
                elif ":" in t:
                    formatted_time = datetime.strptime(t, "%H:%M").time().strftime("%H:%M")
            except Exception:
                formatted_time = None

        return {
            "tool": "create_reminder",
            "arguments": {
                "title": title,
                "due_date": due_date.isoformat(),
                "due_time": formatted_time,
            },
        }

    # 9. List Reminders
    list_rem = _LIST_REMINDERS_RE.search(clean_msg)
    if list_rem:
        modifier = (list_rem.group(1) or "all").lower()
        when_arg = "all"
        if "overdue" in modifier:
            when_arg = "overdue"
        elif "today" in modifier:
            when_arg = "today"
        elif "upcoming" in modifier or "pending" in modifier:
            when_arg = "upcoming"
        return {"tool": "list_reminders", "arguments": {"when": when_arg}}

    return None
