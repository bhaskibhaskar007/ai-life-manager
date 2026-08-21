"""
Analytics MCP tools.

Each opens its own short-lived DB session and delegates to
`AnalyticsService`. `calculate_percentage_change` is the one exception
that needs no session at all — it's a pure calculation the LLM can use
for any two numbers, not just expense data.
"""

from app.database import AsyncSessionLocal
from app.mcp.logging import log_tool_execution
from app.mcp.server import mcp
from app.services.analytics_service import AnalyticsService
from app.utils.parsing import parse_iso_date


@mcp.tool
@log_tool_execution("calculate_weekly_total")
async def calculate_weekly_total(user_id: int, reference_date: str | None = None) -> dict:
    """
    Total spending for the week (Mon–Sun) containing `reference_date`
    (YYYY-MM-DD), or the current week if not given.
    """
    async with AsyncSessionLocal() as session:
        service = AnalyticsService(session)
        result = await service.calculate_weekly_total(
            user_id=user_id, reference=parse_iso_date(reference_date) if reference_date else None
        )
        return {"success": True, **result}


@mcp.tool
@log_tool_execution("calculate_previous_week_total")
async def calculate_previous_week_total(user_id: int, reference_date: str | None = None) -> dict:
    """
    Total spending for the week immediately before the one containing
    `reference_date` (YYYY-MM-DD), or before the current week if not given.
    """
    async with AsyncSessionLocal() as session:
        service = AnalyticsService(session)
        result = await service.calculate_previous_week_total(
            user_id=user_id, reference=parse_iso_date(reference_date) if reference_date else None
        )
        return {"success": True, **result}


@mcp.tool
@log_tool_execution("calculate_percentage_change")
async def calculate_percentage_change(current_amount: float, previous_amount: float) -> dict:
    """
    General-purpose percentage-change calculator: ((current - previous)
    / previous) * 100. Works for any two numbers, not just expenses.
    Returns percentage_change=None if previous_amount is 0 (undefined,
    not infinite).
    """
    result = AnalyticsService.calculate_percentage_change(current_amount, previous_amount)
    return {"success": True, **result}


@mcp.tool
@log_tool_execution("detect_spending_trend")
async def detect_spending_trend(user_id: int, weeks: int = 4) -> dict:
    """
    Analyzes the last N weeks (default 4, 2–26 allowed) of spending
    week-over-week and returns a trend label (increasing/decreasing/
    stable) along with each week's total and percentage change from
    the week before it.
    """
    async with AsyncSessionLocal() as session:
        service = AnalyticsService(session)
        result = await service.detect_spending_trend(user_id=user_id, weeks=weeks)
        return {"success": True, **result}


@mcp.tool
@log_tool_execution("detect_unusual_expense")
async def detect_unusual_expense(
    user_id: int,
    lookback_days: int = 30,
    threshold_multiplier: float = 2.5,
    expense_id: int | None = None,
) -> dict:
    """
    Flags expenses that are unusually high compared to the user's
    typical spending in that same category. An expense is flagged when
    it exceeds `threshold_multiplier` times the category's average
    (default 2.5x) — only for categories with at least 3 other recent
    expenses to compare against. Pass `expense_id` to check one
    specific expense; omit it to scan everything in `lookback_days`
    (default 30).
    """
    async with AsyncSessionLocal() as session:
        service = AnalyticsService(session)
        result = await service.detect_unusual_expense(
            user_id=user_id,
            lookback_days=lookback_days,
            threshold_multiplier=threshold_multiplier,
            expense_id=expense_id,
        )
        return {"success": True, **result}


@mcp.tool
@log_tool_execution("generate_financial_insight")
async def generate_financial_insight(user_id: int) -> dict:
    """
    Combines this-week-vs-last-week comparison, the top spending
    category, and any unusually high expenses into one plain-language
    insight (`insight_text`) plus the underlying numbers it was built
    from. Every number comes from the user's actual recorded expenses
    — nothing is estimated or invented. Labeled informational, not
    financial advice.
    """
    async with AsyncSessionLocal() as session:
        service = AnalyticsService(session)
        result = await service.generate_financial_insight(user_id=user_id)
        return {"success": True, **result}
