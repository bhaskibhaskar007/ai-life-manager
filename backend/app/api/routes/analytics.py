"""
Analytics REST endpoints.
"""

from typing import Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.analytics import (
    CategoryBreakdownResponse,
    CompareWeeklyResponse,
    InsightResponse,
    TrendResponse,
    WeeklyTotalResponse,
)
from app.services.analytics_service import AnalyticsService
from app.services.expense_service import ExpenseService
from app.utils.dates import get_month_range, get_week_range
from app.utils.parsing import parse_iso_date

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/weekly", response_model=WeeklyTotalResponse)
async def get_weekly_total(
    reference_date: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    service = AnalyticsService(db)
    ref = parse_iso_date(reference_date) if reference_date else None
    return await service.calculate_weekly_total(user_id=current_user.id, reference=ref)


@router.get("/comparison", response_model=CompareWeeklyResponse)
async def compare_weekly_expenses(
    reference_date: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    service = ExpenseService(db)
    ref = parse_iso_date(reference_date) if reference_date else None
    return await service.compare_weekly_expenses(user_id=current_user.id, reference=ref)


@router.get("/breakdown", response_model=CategoryBreakdownResponse)
async def get_category_breakdown(
    start_date: str | None = None,
    end_date: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    service = ExpenseService(db)
    parsed_start = parse_iso_date(start_date) if start_date else None
    parsed_end = parse_iso_date(end_date) if end_date else None
    if not parsed_start or not parsed_end:
        start_def, end_def = get_month_range()
        parsed_start = parsed_start or start_def
        parsed_end = parsed_end or end_def
    return await service.get_category_breakdown(user_id=current_user.id, start_date=parsed_start, end_date=parsed_end)


@router.get("/trend", response_model=TrendResponse)
async def get_spending_trend(
    weeks: int = Query(4, ge=2, le=26),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    service = AnalyticsService(db)
    return await service.detect_spending_trend(user_id=current_user.id, weeks=weeks)


@router.get("/insights", response_model=InsightResponse)
async def get_financial_insights(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    service = AnalyticsService(db)
    return await service.generate_financial_insight(user_id=current_user.id)
