"""
Expense service layer.

MCP tools call *this*, never the repositories directly. This is where
input validation lives (amount bounds, etc.) — the LLM can request
anything, but only validated, business-rule-checked calls reach the
database.
"""

from datetime import date, timedelta
from decimal import Decimal, InvalidOperation

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import PaymentMethod
from app.models.expense import Expense
from app.repositories import category_repository, expense_repository
from app.utils.calculations import round_currency, safe_average, safe_percentage_change
from app.utils.dates import get_previous_week_range, get_week_range

MAX_REASONABLE_AMOUNT = Decimal("10000000")  # sanity ceiling, not a business limit


def _to_decimal(amount: float) -> Decimal:
    try:
        value = Decimal(str(amount))
    except InvalidOperation:
        raise ValueError(f"'{amount}' is not a valid amount.") from None
    if value <= 0:
        raise ValueError("Amount must be greater than zero.")
    if value > MAX_REASONABLE_AMOUNT:
        raise ValueError("That amount looks unrealistically large — please double-check it.")
    return value


def _serialize_expense(expense: Expense, category_name: str) -> dict:
    return {
        "id": expense.id,
        "amount": round_currency(expense.amount),
        "category": category_name,
        "description": expense.description,
        "date": expense.date.isoformat(),
        "payment_method": expense.payment_method.value,
        "notes": expense.notes,
    }


class ExpenseService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_expense(
        self,
        *,
        user_id: int,
        amount: float,
        category: str,
        description: str | None = None,
        expense_date: date | None = None,
        payment_method: PaymentMethod = PaymentMethod.OTHER,
        notes: str | None = None,
    ) -> dict:
        decimal_amount = _to_decimal(amount)
        if not category or not category.strip():
            raise ValueError("A category is required.")

        cat = await category_repository.get_or_create_category(self.session, user_id, category)
        expense = await expense_repository.create_expense(
            self.session,
            user_id=user_id,
            category_id=cat.id,
            amount=decimal_amount,
            expense_date=expense_date or date.today(),
            description=description,
            payment_method=payment_method,
            notes=notes,
        )
        return _serialize_expense(expense, cat.name)

    async def get_expenses(
        self,
        *,
        user_id: int,
        start_date: date | None = None,
        end_date: date | None = None,
        category: str | None = None,
        limit: int = 50,
    ) -> list[dict]:
        category_id = None
        if category:
            cat = await category_repository.find_category(self.session, user_id, category)
            if cat is None:
                return []  # unknown category — no matching expenses, not an error
            category_id = cat.id

        expenses = await expense_repository.list_expenses(
            self.session,
            user_id,
            start_date=start_date,
            end_date=end_date,
            category_id=category_id,
            limit=limit,
        )
        categories = {c.id: c.name for c in await category_repository.list_categories(self.session, user_id)}
        return [_serialize_expense(e, categories.get(e.category_id, "Other")) for e in expenses]

    async def update_expense(
        self,
        *,
        user_id: int,
        expense_id: int,
        amount: float | None = None,
        category: str | None = None,
        description: str | None = None,
        expense_date: date | None = None,
        payment_method: PaymentMethod | None = None,
        notes: str | None = None,
    ) -> dict | None:
        category_id = None
        category_name = None
        if category:
            cat = await category_repository.get_or_create_category(self.session, user_id, category)
            category_id = cat.id
            category_name = cat.name

        expense = await expense_repository.update_expense(
            self.session,
            user_id,
            expense_id,
            amount=_to_decimal(amount) if amount is not None else None,
            category_id=category_id,
            description=description,
            date=expense_date,
            payment_method=payment_method,
            notes=notes,
        )
        if expense is None:
            return None

        if category_name is None:
            categories = {c.id: c.name for c in await category_repository.list_categories(self.session, user_id)}
            category_name = categories.get(expense.category_id, "Other")
        return _serialize_expense(expense, category_name)

    async def delete_expense(self, *, user_id: int, expense_id: int) -> bool:
        return await expense_repository.delete_expense(self.session, user_id, expense_id)

    async def get_expense_summary(self, *, user_id: int, start_date: date, end_date: date) -> dict:
        total = await expense_repository.sum_expenses(self.session, user_id, start_date, end_date)
        count = await expense_repository.count_expenses(self.session, user_id, start_date, end_date)
        days = (end_date - start_date).days + 1
        return {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total": round_currency(total),
            "transaction_count": count,
            "average_daily": round_currency(safe_average(total, days)),
        }

    async def get_category_breakdown(self, *, user_id: int, start_date: date, end_date: date) -> dict:
        rows = await expense_repository.sum_by_category(self.session, user_id, start_date, end_date)
        total = sum((amount for _, amount in rows), Decimal(0))
        breakdown = [
            {
                "category": name,
                "total": round_currency(amount),
                "percentage_of_total": round_currency((amount / total * 100)) if total > 0 else 0.0,
            }
            for name, amount in rows
        ]
        return {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total": round_currency(total),
            "breakdown": breakdown,
            "top_category": breakdown[0]["category"] if breakdown else None,
        }

    async def compare_weekly_expenses(self, *, user_id: int, reference: date | None = None) -> dict:
        current_start, current_end = get_week_range(reference)
        previous_start, previous_end = get_previous_week_range(reference)

        current_total = await expense_repository.sum_expenses(self.session, user_id, current_start, current_end)
        previous_total = await expense_repository.sum_expenses(self.session, user_id, previous_start, previous_end)
        change_percent = safe_percentage_change(current_total, previous_total)

        return {
            "current_week": {
                "start": current_start.isoformat(),
                "end": current_end.isoformat(),
                "total": round_currency(current_total),
            },
            "previous_week": {
                "start": previous_start.isoformat(),
                "end": previous_end.isoformat(),
                "total": round_currency(previous_total),
            },
            "change_amount": round_currency(current_total - previous_total),
            "change_percent": round(change_percent, 2) if change_percent is not None else None,
            "note": "No prior-week spending to compare against." if previous_total == 0 else None,
        }

    async def get_spending_trend(self, *, user_id: int, weeks: int = 4) -> dict:
        if weeks < 2 or weeks > 26:
            raise ValueError("weeks must be between 2 and 26.")

        today = date.today()
        weekly_totals = []
        for i in range(weeks - 1, -1, -1):
            ref = today - timedelta(weeks=i)
            start, end = get_week_range(ref)
            total = await expense_repository.sum_expenses(self.session, user_id, start, end)
            weekly_totals.append(
                {"week_start": start.isoformat(), "week_end": end.isoformat(), "total": round_currency(total)}
            )

        mid = len(weekly_totals) // 2
        first_half_avg = sum(w["total"] for w in weekly_totals[:mid]) / mid if mid else 0.0
        second_half_avg = sum(w["total"] for w in weekly_totals[mid:]) / (len(weekly_totals) - mid)

        if first_half_avg == 0:
            trend = "increasing" if second_half_avg > 0 else "stable"
        elif second_half_avg > first_half_avg * 1.1:
            trend = "increasing"
        elif second_half_avg < first_half_avg * 0.9:
            trend = "decreasing"
        else:
            trend = "stable"

        return {"weeks": weekly_totals, "trend": trend}
