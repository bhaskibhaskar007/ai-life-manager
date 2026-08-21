"""Repository for the budgets table."""

from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.budget import Budget
from app.models.enums import BudgetPeriod


async def get_budget_by_category(session: AsyncSession, user_id: int, category_id: int | None) -> Budget | None:
    """category_id=None looks up the user's overall (non-category-specific) budget."""
    stmt = select(Budget).where(Budget.user_id == user_id, Budget.category_id == category_id)
    result = await session.execute(stmt)
    return result.scalars().first()


async def create_budget(
    session: AsyncSession,
    *,
    user_id: int,
    category_id: int | None,
    amount: Decimal,
    period: BudgetPeriod,
    start_date: date,
) -> Budget:
    budget = Budget(user_id=user_id, category_id=category_id, amount=amount, period=period, start_date=start_date)
    session.add(budget)
    await session.commit()
    await session.refresh(budget)
    return budget


async def update_budget(session: AsyncSession, budget: Budget, *, amount: Decimal, period: BudgetPeriod) -> Budget:
    budget.amount = amount
    budget.period = period
    await session.commit()
    await session.refresh(budget)
    return budget


async def list_budgets(session: AsyncSession, user_id: int) -> list[Budget]:
    stmt = (
        select(Budget)
        .where(Budget.user_id == user_id)
        .order_by(Budget.category_id.is_(None).desc(), Budget.id)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())
