"""
Seeds the global default expense categories (user_id = NULL).

Run once after migrations: `python -m app.utils.seed_categories`
Safe to re-run — skips categories that already exist by name.
"""

import asyncio

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.expense import ExpenseCategory

DEFAULT_CATEGORIES = [
    "Food",
    "Transportation",
    "Shopping",
    "Education",
    "Entertainment",
    "Bills",
    "Healthcare",
    "Travel",
    "Subscriptions",
    "Other",
]


async def seed_default_categories() -> None:
    async with AsyncSessionLocal() as session:
        existing = await session.execute(
            select(ExpenseCategory.name).where(ExpenseCategory.user_id.is_(None))
        )
        existing_names = {row[0] for row in existing.all()}

        created = 0
        for name in DEFAULT_CATEGORIES:
            if name not in existing_names:
                session.add(ExpenseCategory(user_id=None, name=name, is_custom=False))
                created += 1

        await session.commit()
        print(f"Seeded {created} default categories ({len(DEFAULT_CATEGORIES) - created} already existed).")


if __name__ == "__main__":
    asyncio.run(seed_default_categories())
