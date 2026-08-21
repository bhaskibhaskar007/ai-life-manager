"""Repository for the user_preferences table."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.preference import UserPreference


async def get_preference(session: AsyncSession, user_id: int, key: str) -> UserPreference | None:
    stmt = select(UserPreference).where(UserPreference.user_id == user_id, UserPreference.key == key)
    result = await session.execute(stmt)
    return result.scalars().first()


async def upsert_preference(session: AsyncSession, user_id: int, key: str, value: str) -> UserPreference:
    existing = await get_preference(session, user_id, key)
    if existing:
        existing.value = value
        await session.commit()
        await session.refresh(existing)
        return existing

    preference = UserPreference(user_id=user_id, key=key, value=value)
    session.add(preference)
    await session.commit()
    await session.refresh(preference)
    return preference


async def list_preferences(session: AsyncSession, user_id: int) -> list[UserPreference]:
    stmt = select(UserPreference).where(UserPreference.user_id == user_id).order_by(UserPreference.key)
    result = await session.execute(stmt)
    return list(result.scalars().all())
