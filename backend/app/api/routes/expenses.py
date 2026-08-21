"""
Expenses REST endpoints.

Enforces strict user isolation — all queries automatically scope to current_user.id.
"""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.enums import PaymentMethod
from app.models.user import User
from app.repositories import category_repository
from app.schemas.expense import (
    CategoryResponse,
    ExpenseCreateRequest,
    ExpenseResponse,
    ExpenseUpdateRequest,
)
from app.services.expense_service import ExpenseService
from app.utils.parsing import parse_iso_date

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.post("", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_expense(
    request: ExpenseCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    service = ExpenseService(db)
    parsed_date = parse_iso_date(request.expense_date) if request.expense_date else None
    try:
        payment_enum = PaymentMethod(request.payment_method.lower())
    except ValueError:
        payment_enum = PaymentMethod.OTHER

    try:
        return await service.add_expense(
            user_id=current_user.id,
            amount=request.amount,
            category=request.category,
            description=request.description,
            expense_date=parsed_date,
            payment_method=payment_enum,
            notes=request.notes,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from None


@router.get("", response_model=list[ExpenseResponse])
async def list_expenses(
    category: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    payment_method: str | None = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    service = ExpenseService(db)
    parsed_start = parse_iso_date(start_date) if start_date else None
    parsed_end = parse_iso_date(end_date) if end_date else None

    return await service.get_expenses(
        user_id=current_user.id,
        category=category,
        start_date=parsed_start,
        end_date=parsed_end,
        limit=limit,
    )


@router.get("/categories", response_model=list[CategoryResponse])
async def list_categories(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[CategoryResponse]:
    cats = await category_repository.list_categories(db, current_user.id)
    return [CategoryResponse(id=c.id, name=c.name, is_custom=c.is_custom) for c in cats]


@router.get("/summary")
async def get_expense_summary(
    start_date: str | None = None,
    end_date: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    service = ExpenseService(db)
    parsed_start = parse_iso_date(start_date) if start_date else None
    parsed_end = parse_iso_date(end_date) if end_date else None
    return await service.get_expense_summary(user_id=current_user.id, start_date=parsed_start, end_date=parsed_end)


@router.put("/{expense_id}", response_model=ExpenseResponse)
async def update_expense(
    expense_id: int,
    request: ExpenseUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    service = ExpenseService(db)
    parsed_date = parse_iso_date(request.expense_date) if request.expense_date else None
    payment_enum = None
    if request.payment_method:
        try:
            payment_enum = PaymentMethod(request.payment_method.lower())
        except ValueError:
            pass

    try:
        updated = await service.update_expense(
            user_id=current_user.id,
            expense_id=expense_id,
            amount=request.amount,
            category=request.category,
            description=request.description,
            expense_date=parsed_date,
            payment_method=payment_enum,
            notes=request.notes,
        )
        if not updated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found.")
        return updated
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from None


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense(
    expense_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    service = ExpenseService(db)
    deleted = await service.delete_expense(user_id=current_user.id, expense_id=expense_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found.")
