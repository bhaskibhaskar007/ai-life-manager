"""Repository for expense_categories: default (global) + per-user custom categories."""

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.expense import ExpenseCategory


async def find_category(session: AsyncSession, user_id: int, name: str) -> ExpenseCategory | None:
    """Case-insensitive lookup across global defaults (user_id NULL) and this user's custom categories."""
    stmt = select(ExpenseCategory).where(
        or_(ExpenseCategory.user_id == user_id, ExpenseCategory.user_id.is_(None)),
        func.lower(ExpenseCategory.name) == name.strip().lower(),
    )
    result = await session.execute(stmt)
    return result.scalars().first()


async def get_or_create_category(session: AsyncSession, user_id: int, name: str) -> ExpenseCategory:
    """Used by add_expense: an unrecognized category name becomes a new custom category."""
    existing = await find_category(session, user_id, name)
    if existing:
        return existing

    category = ExpenseCategory(user_id=user_id, name=name.strip().title(), is_custom=True)
    session.add(category)
    await session.flush()  # assigns category.id without committing the whole transaction yet
    return category


async def list_categories(session: AsyncSession, user_id: int) -> list[ExpenseCategory]:
    stmt = (
        select(ExpenseCategory)
        .where(or_(ExpenseCategory.user_id == user_id, ExpenseCategory.user_id.is_(None)))
        .order_by(ExpenseCategory.name)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())
