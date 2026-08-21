"""MCP budget tools."""

from app.database import AsyncSessionLocal
from app.mcp.logging import log_tool_execution
from app.mcp.server import mcp
from app.services.budget_service import BudgetService
from app.utils.parsing import parse_budget_period, parse_iso_date


@mcp.tool
@log_tool_execution("create_budget")
async def create_budget(
    user_id: int,
    amount: float,
    period: str = "monthly",
    category: str | None = None,
    start_date: str | None = None,
) -> dict:
    """
    Set a budget. Omit `category` for an overall budget across all
    spending; provide it (e.g. 'Food') for a category-specific budget.
    `period` is one of: weekly, monthly, yearly — the budget tracks
    spending in the *current* calendar week/month/year, resetting
    automatically each period. Calling this again for the same
    category/overall scope updates the existing budget instead of
    creating a duplicate.
    """
    async with AsyncSessionLocal() as session:
        service = BudgetService(session)
        result = await service.create_budget(
            user_id=user_id,
            amount=amount,
            period=parse_budget_period(period),
            category=category,
            start_date=parse_iso_date(start_date) if start_date else None,
        )
        return {"success": True, "budget": result}


@mcp.tool
@log_tool_execution("get_budget")
async def get_budget(user_id: int, category: str | None = None) -> dict:
    """Look up an existing budget. Omit `category` for the overall budget."""
    async with AsyncSessionLocal() as session:
        service = BudgetService(session)
        result = await service.get_budget(user_id=user_id, category=category)
        if result is None:
            scope = f"'{category}'" if category else "an overall"
            return {"success": False, "error": f"No budget has been set for {scope} category yet."}
        return {"success": True, "budget": result}


@mcp.tool
@log_tool_execution("calculate_remaining_budget")
async def calculate_remaining_budget(user_id: int, category: str | None = None) -> dict:
    """
    How much of a budget is left in the current period: amount
    spent so far, amount remaining, and percentage used. Omit
    `category` for the overall budget.
    """
    async with AsyncSessionLocal() as session:
        service = BudgetService(session)
        result = await service.calculate_remaining_budget(user_id=user_id, category=category)
        return {"success": True, **result}


@mcp.tool
@log_tool_execution("detect_budget_risk")
async def detect_budget_risk(user_id: int, threshold_percent: float = 80.0) -> dict:
    """
    Checks all of the user's budgets and flags any at or above
    `threshold_percent` of their limit for the current period (default
    80%). Each budget's status is one of: on_track, at_risk, exceeded.
    """
    async with AsyncSessionLocal() as session:
        service = BudgetService(session)
        result = await service.detect_budget_risk(user_id=user_id, threshold_percent=threshold_percent)
        return {"success": True, **result}
