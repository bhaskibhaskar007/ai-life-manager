"""Repository for the expenses table: CRUD plus the aggregate queries expense/analytics tools need."""

from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import PaymentMethod
from app.models.expense import Expense, ExpenseCategory


async def create_expense(
    session: AsyncSession,
    *,
    user_id: int,
    category_id: int,
    amount: Decimal,
    expense_date: date,
    description: str | None,
    payment_method: PaymentMethod,
    notes: str | None,
) -> Expense:
    expense = Expense(
        user_id=user_id,
        category_id=category_id,
        amount=amount,
        date=expense_date,
        description=description,
        payment_method=payment_method,
        notes=notes,
    )
    session.add(expense)
    await session.commit()
    await session.refresh(expense)
    return expense


async def get_expense(session: AsyncSession, user_id: int, expense_id: int) -> Expense | None:
    stmt = select(Expense).where(Expense.id == expense_id, Expense.user_id == user_id)
    result = await session.execute(stmt)
    return result.scalars().first()


async def list_expenses(
    session: AsyncSession,
    user_id: int,
    *,
    start_date: date | None = None,
    end_date: date | None = None,
    category_id: int | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[Expense]:
    stmt = select(Expense).where(Expense.user_id == user_id)
    if start_date is not None:
        stmt = stmt.where(Expense.date >= start_date)
    if end_date is not None:
        stmt = stmt.where(Expense.date <= end_date)
    if category_id is not None:
        stmt = stmt.where(Expense.category_id == category_id)
    stmt = stmt.order_by(Expense.date.desc(), Expense.id.desc()).limit(limit).offset(offset)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def update_expense(session: AsyncSession, user_id: int, expense_id: int, **fields) -> Expense | None:
    expense = await get_expense(session, user_id, expense_id)
    if expense is None:
        return None
    for key, value in fields.items():
        if value is not None:
            setattr(expense, key, value)
    await session.commit()
    await session.refresh(expense)
    return expense


async def delete_expense(session: AsyncSession, user_id: int, expense_id: int) -> bool:
    expense = await get_expense(session, user_id, expense_id)
    if expense is None:
        return False
    await session.delete(expense)
    await session.commit()
    return True


async def sum_expenses(
    session: AsyncSession,
    user_id: int,
    start_date: date,
    end_date: date,
    category_id: int | None = None,
) -> Decimal:
    stmt = select(func.coalesce(func.sum(Expense.amount), 0)).where(
        Expense.user_id == user_id, Expense.date >= start_date, Expense.date <= end_date
    )
    if category_id is not None:
        stmt = stmt.where(Expense.category_id == category_id)
    result = await session.execute(stmt)
    return Decimal(result.scalar_one())


async def count_expenses(session: AsyncSession, user_id: int, start_date: date, end_date: date) -> int:
    stmt = select(func.count(Expense.id)).where(
        Expense.user_id == user_id, Expense.date >= start_date, Expense.date <= end_date
    )
    result = await session.execute(stmt)
    return result.scalar_one()


async def sum_by_category(
    session: AsyncSession, user_id: int, start_date: date, end_date: date
) -> list[tuple[str, Decimal]]:
    """Returns [(category_name, total), ...] sorted highest spend first."""
    stmt = (
        select(ExpenseCategory.name, func.coalesce(func.sum(Expense.amount), 0))
        .join(Expense, Expense.category_id == ExpenseCategory.id)
        .where(Expense.user_id == user_id, Expense.date >= start_date, Expense.date <= end_date)
        .group_by(ExpenseCategory.name)
        .order_by(func.sum(Expense.amount).desc())
    )
    result = await session.execute(stmt)
    return [(name, Decimal(total)) for name, total in result.all()]
