"""
Budgets REST endpoints.
"""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.enums import BudgetPeriod
from app.models.user import User
from app.repositories import budget_repository
from app.schemas.budget import BudgetCreateRequest, BudgetResponse
from app.services.budget_service import BudgetService

router = APIRouter(prefix="/budgets", tags=["budgets"])


@router.post("", response_model=BudgetResponse, status_code=status.HTTP_200_OK)
async def upsert_budget(
    request: BudgetCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    service = BudgetService(db)
    try:
        period_enum = BudgetPeriod(request.period.lower())
    except ValueError:
        period_enum = BudgetPeriod.MONTHLY

    try:
        return await service.create_budget(
            user_id=current_user.id,
            amount=request.amount,
            category=request.category,
            period=period_enum,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from None


@router.get("", response_model=list[BudgetResponse])
async def list_budgets(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    service = BudgetService(db)
    budgets = await budget_repository.list_budgets(db, current_user.id)
    return [await service._evaluate_budget(b) for b in budgets]


@router.get("/remaining")
async def get_remaining_budget(
    category: str | None = Query(None, description="Category name (omit for overall budget)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    service = BudgetService(db)
    try:
        return await service.calculate_remaining_budget(user_id=current_user.id, category=category)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.get("/risk")
async def detect_budget_risk(
    threshold_percent: float = Query(80.0, ge=1.0, le=100.0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    service = BudgetService(db)
    return await service.detect_budget_risk(user_id=current_user.id, threshold_percent=threshold_percent)
