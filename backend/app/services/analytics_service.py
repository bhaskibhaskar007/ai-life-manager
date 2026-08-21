"""
Analytics service layer.

Distinct from ExpenseService: these are lower-level, composable
calculation primitives (a single week's total, a raw percentage-change
calculation, trend/anomaly detection) that other tools — like
`generate_financial_insight` — build on top of. MCP tools call this,
never the repositories directly.
"""

from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import category_repository, expense_repository
from app.services.expense_service import ExpenseService
from app.utils.calculations import round_currency, safe_percentage_change
from app.utils.dates import get_previous_week_range, get_week_range

MIN_CATEGORY_HISTORY = 3  # minimum prior expenses in a category before we'll judge one "unusual"


class AnalyticsService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.expense_service = ExpenseService(session)

    async def calculate_weekly_total(self, *, user_id: int, reference: date | None = None) -> dict:
        start, end = get_week_range(reference)
        total = await expense_repository.sum_expenses(self.session, user_id, start, end)
        return {"week_start": start.isoformat(), "week_end": end.isoformat(), "total": round_currency(total)}

    async def calculate_previous_week_total(self, *, user_id: int, reference: date | None = None) -> dict:
        start, end = get_previous_week_range(reference)
        total = await expense_repository.sum_expenses(self.session, user_id, start, end)
        return {"week_start": start.isoformat(), "week_end": end.isoformat(), "total": round_currency(total)}

    @staticmethod
    def calculate_percentage_change(current_amount: float, previous_amount: float) -> dict:
        """
        Pure calculation, no database access — lets the LLM ask
        'what's the percentage change between X and Y' for any two
        numbers, not just week totals.
        """
        current = Decimal(str(current_amount))
        previous = Decimal(str(previous_amount))
        change = safe_percentage_change(current, previous)

        if change is None:
            direction = None
        elif change > 0:
            direction = "increase"
        elif change < 0:
            direction = "decrease"
        else:
            direction = "no change"

        return {
            "current_amount": round_currency(current),
            "previous_amount": round_currency(previous),
            "percentage_change": round(change, 2) if change is not None else None,
            "direction": direction,
            "note": "Previous amount was 0 — percentage change is undefined." if previous == 0 else None,
        }

    async def detect_spending_trend(self, *, user_id: int, weeks: int = 4) -> dict:
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

        week_over_week_changes = []
        for prev_week, curr_week in zip(weekly_totals, weekly_totals[1:]):
            pct = safe_percentage_change(Decimal(str(curr_week["total"])), Decimal(str(prev_week["total"])))
            week_over_week_changes.append(
                {
                    "from_week": prev_week["week_start"],
                    "to_week": curr_week["week_start"],
                    "percentage_change": round(pct, 2) if pct is not None else None,
                }
            )

        increases = sum(1 for c in week_over_week_changes if (c["percentage_change"] or 0) > 0)
        decreases = sum(1 for c in week_over_week_changes if (c["percentage_change"] or 0) < 0)
        if increases > decreases:
            trend = "increasing"
        elif decreases > increases:
            trend = "decreasing"
        else:
            trend = "stable"

        return {"weekly_totals": weekly_totals, "week_over_week_changes": week_over_week_changes, "trend": trend}

    async def detect_unusual_expense(
        self,
        *,
        user_id: int,
        lookback_days: int = 30,
        threshold_multiplier: float = 2.5,
        expense_id: int | None = None,
    ) -> dict:
        if threshold_multiplier <= 1:
            raise ValueError("threshold_multiplier must be greater than 1.")
        if lookback_days < 1 or lookback_days > 365:
            raise ValueError("lookback_days must be between 1 and 365.")

        end = date.today()
        start = end - timedelta(days=lookback_days)
        window_expenses = await expense_repository.list_expenses(
            self.session, user_id, start_date=start, end_date=end, limit=1000
        )

        if expense_id is not None:
            target = await expense_repository.get_expense(self.session, user_id, expense_id)
            if target is None:
                raise ValueError(f"No expense with id {expense_id} found for this user.")
            targets = [target]
            # Make sure the target is included in its category's peer pool
            # even if it happens to fall outside the lookback window.
            if target.id not in {e.id for e in window_expenses}:
                window_expenses = window_expenses + [target]
        else:
            targets = window_expenses

        by_category: dict[int, list] = {}
        for expense in window_expenses:
            by_category.setdefault(expense.category_id, []).append(expense)

        categories = {c.id: c.name for c in await category_repository.list_categories(self.session, user_id)}

        flagged = []
        for target in targets:
            peers = [e for e in by_category.get(target.category_id, []) if e.id != target.id]
            if len(peers) < MIN_CATEGORY_HISTORY:
                continue  # not enough history in this category to judge yet

            mean_amount = sum((p.amount for p in peers), Decimal(0)) / len(peers)
            if mean_amount > 0 and target.amount > mean_amount * Decimal(str(threshold_multiplier)):
                flagged.append(
                    {
                        "expense_id": target.id,
                        "amount": round_currency(target.amount),
                        "category": categories.get(target.category_id, "Other"),
                        "date": target.date.isoformat(),
                        "typical_amount": round_currency(mean_amount),
                        "times_higher_than_typical": round(float(target.amount / mean_amount), 2),
                    }
                )

        return {
            "lookback_days": lookback_days,
            "threshold_multiplier": threshold_multiplier,
            "count": len(flagged),
            "unusual_expenses": flagged,
        }

    async def generate_financial_insight(self, *, user_id: int) -> dict:
        comparison = await self.expense_service.compare_weekly_expenses(user_id=user_id)
        week_start, week_end = get_week_range()
        breakdown = await self.expense_service.get_category_breakdown(
            user_id=user_id, start_date=week_start, end_date=week_end
        )
        unusual = await self.detect_unusual_expense(user_id=user_id, lookback_days=30, threshold_multiplier=2.5)

        change_percent = comparison["change_percent"]
        top_category = breakdown["top_category"]

        if change_percent is None:
            text = "There isn't enough prior-week spending data yet to compare a trend."
        else:
            direction = "increased" if change_percent >= 0 else "decreased"
            text = f"Your spending has {direction} by approximately {abs(change_percent):.1f}% compared with last week"
            text += f", with {top_category} as your largest spending category this week." if top_category else "."

        if unusual["count"] > 0:
            text += f" {unusual['count']} unusually high expense(s) were detected in the last 30 days."

        return {
            "weekly_comparison": comparison,
            "top_category": top_category,
            "unusual_expenses": unusual["unusual_expenses"],
            "insight_text": text,
            "disclaimer": "This is an informational observation based on your recorded expenses, not financial advice.",
        }
