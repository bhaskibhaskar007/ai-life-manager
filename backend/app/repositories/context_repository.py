"""Repository for the conversation_context table."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.context import ConversationContext


async def create_context(session: AsyncSession, user_id: int, summary: str) -> ConversationContext:
    context = ConversationContext(user_id=user_id, summary=summary)
    session.add(context)
    await session.commit()
    await session.refresh(context)
    return context


async def list_recent_context(session: AsyncSession, user_id: int, limit: int = 10) -> list[ConversationContext]:
    stmt = (
        select(ConversationContext)
        .where(ConversationContext.user_id == user_id)
        .order_by(ConversationContext.created_at.desc())
        .limit(limit)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def search_context(session: AsyncSession, user_id: int, query: str, limit: int = 5) -> list[ConversationContext]:
    """
    Simple keyword substring search over stored summaries (case-insensitive).

    NOTE: this is intentionally basic — the `embedding` column on
    ConversationContext exists but is unused so a future phase can
    upgrade this to real vector similarity search (e.g. pgvector)
    without changing the table schema or this function's signature.
    """
    stmt = (
        select(ConversationContext)
        .where(
            ConversationContext.user_id == user_id,
            ConversationContext.summary.ilike(f"%{query}%"),
        )
        .order_by(ConversationContext.created_at.desc())
        .limit(limit)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())
