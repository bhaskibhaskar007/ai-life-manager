"""
Budget service layer.

A "period" (weekly/monthly/yearly) is evaluated against the *current*
calendar week/month/year — not a custom recurrence anchored to
`start_date`. This keeps the mental model simple: a monthly budget
always tracks spending in the current calendar month, resetting
automatically, which matches how people actually think about budgets
("my monthly food budget") without needing background jobs to roll
periods over.
"""

from datetime import date
from decimal import Decimal, InvalidOperation

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.budget import Budget
from app.models.enums import BudgetPeriod
from app.repositories import budget_repository, category_repository, expense_repository
from app.utils.calculations import round_currency
from app.utils.dates import get_month_range, get_week_range, get_year_range

MAX_REASONABLE_AMOUNT = Decimal("10000000")


def _to_decimal(amount: float) -> Decimal:
    try:
        value = Decimal(str(amount))
    except InvalidOperation:
        raise ValueError(f"'{amount}' is not a valid amount.") from None
    if value <= 0:
        raise ValueError("Budget amount must be greater than zero.")
    if value > MAX_REASONABLE_AMOUNT:
        raise ValueError("That amount looks unrealistically large — please double-check it.")
    return value


def _period_range(period: BudgetPeriod) -> tuple[date, date]:
    if period == BudgetPeriod.WEEKLY:
        return get_week_range()
    if period == BudgetPeriod.MONTHLY:
        return get_month_range()
    return get_year_range()


class BudgetService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _resolve_category_id(self, user_id: int, category: str | None) -> tuple[int | None, str | None]:
        if not category:
            return None, None
        cat = await category_repository.get_or_create_category(self.session, user_id, category)
        return cat.id, cat.name

    async def _serialize_budget(self, budget: Budget) -> dict:
        category_name = None
        if budget.category_id is not None:
            categories = {c.id: c.name for c in await category_repository.list_categories(self.session, budget.user_id)}
            category_name = categories.get(budget.category_id, "Other")
        return {
            "id": budget.id,
            "category": category_name,  # None means an overall (all-category) budget
            "amount": round_currency(budget.amount),
            "period": budget.period.value,
            "start_date": budget.start_date.isoformat(),
        }

    async def create_budget(
        self,
        *,
        user_id: int,
        amount: float,
        period: BudgetPeriod = BudgetPeriod.MONTHLY,
        category: str | None = None,
        start_date: date | None = None,
    ) -> dict:
        decimal_amount = _to_decimal(amount)
        category_id, _ = await self._resolve_category_id(user_id, category)

        existing = await budget_repository.get_budget_by_category(self.session, user_id, category_id)
        if existing:
            budget = await budget_repository.update_budget(self.session, existing, amount=decimal_amount, period=period)
            was_updated = True
        else:
            budget = await budget_repository.create_budget(
                self.session,
                user_id=user_id,
                category_id=category_id,
                amount=decimal_amount,
                period=period,
                start_date=start_date or date.today(),
            )
            was_updated = False

        result = await self._serialize_budget(budget)
        result["was_updated"] = was_updated
        return result

    async def get_budget(self, *, user_id: int, category: str | None = None) -> dict | None:
        category_id, _ = await self._resolve_category_id(user_id, category)
        budget = await budget_repository.get_budget_by_category(self.session, user_id, category_id)
        if budget is None:
            return None
        return await self._serialize_budget(budget)

    async def _evaluate_budget(self, budget: Budget) -> dict:
        start, end = _period_range(budget.period)
        spent = await expense_repository.sum_expenses(
            self.session, budget.user_id, start, end, category_id=budget.category_id
        )
        remaining = budget.amount - spent
        percentage_used = round(float(spent / budget.amount * 100), 2)

        if percentage_used > 100:
            status = "exceeded"
        elif percentage_used >= 80:
            status = "at_risk"
        else:
            status = "on_track"

        serialized = await self._serialize_budget(budget)
        serialized.update(
            {
                "period_start": start.isoformat(),
                "period_end": end.isoformat(),
                "spent": round_currency(spent),
                "remaining": round_currency(remaining),
                "percentage_used": percentage_used,
                "status": status,
            }
        )
        return serialized

    async def calculate_remaining_budget(self, *, user_id: int, category: str | None = None) -> dict:
        category_id, category_name = await self._resolve_category_id(user_id, category)
        budget = await budget_repository.get_budget_by_category(self.session, user_id, category_id)
        if budget is None:
            scope = f"'{category_name}'" if category_name else "an overall"
            raise ValueError(f"No budget has been set for {scope} category yet.")
        return await self._evaluate_budget(budget)

    async def detect_budget_risk(self, *, user_id: int, threshold_percent: float = 80.0) -> dict:
        if threshold_percent < 1 or threshold_percent > 100:
            raise ValueError("threshold_percent must be between 1 and 100.")

        budgets = await budget_repository.list_budgets(self.session, user_id)
        evaluated = [await self._evaluate_budget(b) for b in budgets]
        at_risk = [b for b in evaluated if b["percentage_used"] >= threshold_percent]

        return {
            "threshold_percent": threshold_percent,
            "budgets_evaluated": len(evaluated),
            "at_risk_count": len(at_risk),
            "budgets": evaluated,
        }
