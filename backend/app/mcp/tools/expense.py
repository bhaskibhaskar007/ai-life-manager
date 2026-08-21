"""
Expense MCP tools.

Every tool here opens its own short-lived DB session (MCP tools don't
get FastAPI's request-scoped dependency injection), delegates all
business logic to `ExpenseService`, and never touches the database or
repositories directly.
"""

from app.database import AsyncSessionLocal
from app.mcp.logging import log_tool_execution
from app.mcp.server import mcp
from app.models.enums import PaymentMethod
from app.services.expense_service import ExpenseService
from app.utils.dates import get_week_range
from app.utils.parsing import parse_iso_date, parse_payment_method


@mcp.tool
@log_tool_execution("add_expense")
async def add_expense(
    user_id: int,
    amount: float,
    category: str,
    description: str | None = None,
    date: str | None = None,
    payment_method: str = "other",
    notes: str | None = None,
) -> dict:
    """
    Record a new expense. `date` must be YYYY-MM-DD if given (defaults
    to today). `category` can be any name — if it doesn't match an
    existing category, a new custom one is created automatically.
    `payment_method` is one of: cash, card, upi, net_banking, wallet, other.
    """
    async with AsyncSessionLocal() as session:
        service = ExpenseService(session)
        result = await service.add_expense(
            user_id=user_id,
            amount=amount,
            category=category,
            description=description,
            expense_date=parse_iso_date(date) if date else None,
            payment_method=parse_payment_method(payment_method),
            notes=notes,
        )
        return {"success": True, "expense": result}


@mcp.tool
@log_tool_execution("get_expenses")
async def get_expenses(
    user_id: int,
    start_date: str | None = None,
    end_date: str | None = None,
    category: str | None = None,
    limit: int = 50,
) -> dict:
    """
    List the user's expenses, optionally filtered by date range
    (YYYY-MM-DD) and/or category name. Returns most recent first.
    """
    async with AsyncSessionLocal() as session:
        service = ExpenseService(session)
        expenses = await service.get_expenses(
            user_id=user_id,
            start_date=parse_iso_date(start_date) if start_date else None,
            end_date=parse_iso_date(end_date) if end_date else None,
            category=category,
            limit=limit,
        )
        return {"success": True, "count": len(expenses), "expenses": expenses}


@mcp.tool
@log_tool_execution("update_expense")
async def update_expense(
    user_id: int,
    expense_id: int,
    amount: float | None = None,
    category: str | None = None,
    description: str | None = None,
    date: str | None = None,
    payment_method: str | None = None,
    notes: str | None = None,
) -> dict:
    """
    Update one or more fields of an existing expense. Only fields you
    provide are changed. Returns an error if the expense doesn't exist
    or doesn't belong to this user.
    """
    async with AsyncSessionLocal() as session:
        service = ExpenseService(session)
        result = await service.update_expense(
            user_id=user_id,
            expense_id=expense_id,
            amount=amount,
            category=category,
            description=description,
            expense_date=parse_iso_date(date) if date else None,
            payment_method=parse_payment_method(payment_method) if payment_method else None,
            notes=notes,
        )
        if result is None:
            return {"success": False, "error": f"No expense with id {expense_id} found for this user."}
        return {"success": True, "expense": result}


@mcp.tool
@log_tool_execution("delete_expense")
async def delete_expense(user_id: int, expense_id: int) -> dict:
    """Permanently delete an expense by id. Returns an error if it doesn't exist for this user."""
    async with AsyncSessionLocal() as session:
        service = ExpenseService(session)
        deleted = await service.delete_expense(user_id=user_id, expense_id=expense_id)
        if not deleted:
            return {"success": False, "error": f"No expense with id {expense_id} found for this user."}
        return {"success": True, "deleted_expense_id": expense_id}


@mcp.tool
@log_tool_execution("get_expense_summary")
async def get_expense_summary(
    user_id: int,
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict:
    """
    Total spending, transaction count, and average daily spend over a
    date range (YYYY-MM-DD). Defaults to the current week (Mon–Sun) if
    no range is given.
    """
    async with AsyncSessionLocal() as session:
        service = ExpenseService(session)
        if start_date and end_date:
            start, end = parse_iso_date(start_date), parse_iso_date(end_date)
        else:
            start, end = get_week_range()
        result = await service.get_expense_summary(user_id=user_id, start_date=start, end_date=end)
        return {"success": True, "summary": result}


@mcp.tool
@log_tool_execution("get_category_breakdown")
async def get_category_breakdown(
    user_id: int,
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict:
    """
    Spending broken down by category over a date range (YYYY-MM-DD),
    each with its share of the total. Defaults to the current week.
    """
    async with AsyncSessionLocal() as session:
        service = ExpenseService(session)
        if start_date and end_date:
            start, end = parse_iso_date(start_date), parse_iso_date(end_date)
        else:
            start, end = get_week_range()
        result = await service.get_category_breakdown(user_id=user_id, start_date=start, end_date=end)
        return {"success": True, **result}


@mcp.tool
@log_tool_execution("compare_weekly_expenses")
async def compare_weekly_expenses(user_id: int) -> dict:
    """
    Compares this week's spending (Mon–Sun) against last week's:
    totals, the difference, and percentage change. Use this for
    'how does this week compare to last week' style questions.
    """
    async with AsyncSessionLocal() as session:
        service = ExpenseService(session)
        result = await service.compare_weekly_expenses(user_id=user_id)
        return {"success": True, **result}


@mcp.tool
@log_tool_execution("get_spending_trend")
async def get_spending_trend(user_id: int, weeks: int = 4) -> dict:
    """
    Weekly spending totals for the last N weeks (default 4, 2–26
    allowed) plus a simple trend label: increasing, decreasing, or
    stable. Use this for 'how has my spending been trending' questions.
    """
    async with AsyncSessionLocal() as session:
        service = ExpenseService(session)
        result = await service.get_spending_trend(user_id=user_id, weeks=weeks)
        return {"success": True, **result}
