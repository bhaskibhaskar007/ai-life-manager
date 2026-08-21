"""
Conversation context model.

Stores short, non-sensitive *summaries* of past interactions (e.g. "user
usually asks about weekly spending on Mondays") that the `retrieve_relevant_context`
MCP tool can surface to the LLM — not full raw chat transcripts.
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ConversationContext(Base):
    __tablename__ = "conversation_context"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    summary: Mapped[str] = mapped_column(Text, nullable=False)
    # Reserved for a future vector-similarity search upgrade (Phase-future,
    # e.g. pgvector); left nullable so it can be added without a rewrite.
    embedding: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )

    user: Mapped["User"] = relationship(back_populates="contexts")

    def __repr__(self) -> str:
        return f"<ConversationContext id={self.id} user_id={self.user_id}>"
