"""Analytics schemas."""

from typing import Any
from pydantic import BaseModel


class WeeklyTotalResponse(BaseModel):
    week_start: str
    week_end: str
    total: float


class CompareWeeklyResponse(BaseModel):
    current_week: WeeklyTotalResponse
    previous_week: WeeklyTotalResponse
    difference: float
    change_percent: float | None
    direction: str | None


class CategoryBreakdownItem(BaseModel):
    category: str
    total: float
    percentage: float
    count: int


class CategoryBreakdownResponse(BaseModel):
    start_date: str
    end_date: str
    total_spent: float
    category_count: int
    top_category: str | None
    categories: list[CategoryBreakdownItem]


class TrendResponse(BaseModel):
    weekly_totals: list[dict[str, Any]]
    week_over_week_changes: list[dict[str, Any]]
    trend: str


class InsightResponse(BaseModel):
    weekly_comparison: dict[str, Any]
    top_category: str | None
    unusual_expenses: list[dict[str, Any]]
    insight_text: str
    disclaimer: str
