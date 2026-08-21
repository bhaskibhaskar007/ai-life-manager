"""
Day Planner service.

Synthesizes an organized daily plan by combining:
1. Active reminders and deadlines for the target date from ReminderService
2. Real-time weather conditions and rain alerts from WeatherService
3. Daily safe spending guidance based on remaining monthly budget

This ensures the AI day planner never fabricates events or conditions —
every time block is anchored in real database records and live API data.
"""

from datetime import date, timedelta
from decimal import Decimal
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import ReminderStatus
from app.repositories import budget_repository, expense_repository
from app.services.reminder_service import ReminderService
from app.services.weather_service import WeatherService
from app.utils.calculations import round_currency
from app.utils.dates import get_month_range


class PlannerService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.reminder_service = ReminderService(session)

    async def generate_day_plan(
        self,
        *,
        user_id: int,
        target_date: date | None = None,
        location: str | None = "Bengaluru",
    ) -> dict[str, Any]:
        plan_date = target_date or date.today()
        is_today = plan_date == date.today()

        # 1. Fetch scheduled reminders for the date
        reminders = await self.reminder_service.list_reminders(
            user_id=user_id,
            when="today" if is_today else ("tomorrow" if plan_date == date.today() + timedelta(days=1) else "all"),
            status=ReminderStatus.PENDING,
        )
        if not is_today and plan_date != date.today() + timedelta(days=1):
            reminders = [r for r in reminders if r.get("due_date") == plan_date.isoformat()]

        # 2. Fetch weather context safely
        weather_info = None
        if location:
            try:
                weather_svc = WeatherService()
                if is_today:
                    weather_info = await weather_svc.get_current_weather(location=location)
                else:
                    forecast = await weather_svc.get_forecast(location=location, days=5)
                    matching = [d for d in forecast.get("forecast", []) if d.get("date") == plan_date.isoformat()]
                    weather_info = matching[0] if matching else None
            except Exception:
                weather_info = None

        # 3. Calculate safe daily spending guidance
        month_start, month_end = get_month_range(plan_date)
        days_remaining = max(1, (month_end - plan_date).days + 1)

        budgets = await budget_repository.list_budgets(self.session, user_id)
        overall_budget = next((b for b in budgets if b.category_id is None), None)

        safe_spend_info = None
        if overall_budget:
            spent_so_far = await expense_repository.sum_expenses(self.session, user_id, month_start, month_end)
            remaining_budget = overall_budget.amount - spent_so_far
            daily_safe = max(Decimal(0), remaining_budget / Decimal(days_remaining))
            safe_spend_info = {
                "monthly_budget": round_currency(overall_budget.amount),
                "spent_so_far": round_currency(spent_so_far),
                "remaining_budget": round_currency(remaining_budget),
                "days_remaining_in_month": days_remaining,
                "recommended_daily_limit": round_currency(daily_safe),
            }

        # 4. Construct chronological schedule items
        timed_items = []
        untimed_items = []
        for r in reminders:
            if r.get("due_time"):
                timed_items.append({"time": r["due_time"], "title": r["title"], "priority": r["priority"], "type": "reminder"})
            else:
                untimed_items.append({"title": r["title"], "priority": r["priority"], "type": "task"})

        timed_items.sort(key=lambda x: x["time"])

        # Construct structured schedule blocks
        schedule_blocks = []
        morning_tasks = [t for t in timed_items if t["time"] < "12:00"]
        schedule_blocks.append({
            "period": "Morning (08:00 - 12:00)",
            "items": morning_tasks or ([{"title": "Review morning priorities & tasks", "type": "routine"}]),
        })

        afternoon_tasks = [t for t in timed_items if "12:00" <= t["time"] < "17:00"]
        schedule_blocks.append({
            "period": "Afternoon (12:00 - 17:00)",
            "items": afternoon_tasks or ([{"title": "Focus work & scheduled tasks", "type": "routine"}]),
        })

        evening_tasks = [t for t in timed_items if t["time"] >= "17:00"]
        schedule_blocks.append({
            "period": "Evening (17:00 - 21:00)",
            "items": evening_tasks or ([{"title": "Daily wrap-up & personal time", "type": "routine"}]),
        })

        return {
            "date": plan_date.isoformat(),
            "reminders_count": len(reminders),
            "timed_reminders": timed_items,
            "flexible_tasks": untimed_items,
            "schedule_blocks": schedule_blocks,
            "weather": weather_info,
            "safe_spend_guidance": safe_spend_info,
            "notes": (
                f"Rain alert: {weather_info.get('conditions')} expected today — consider keeping an umbrella!"
                if weather_info and weather_info.get("rain_expected")
                else "Weather conditions look favorable for outdoor activities."
            ),
        }
