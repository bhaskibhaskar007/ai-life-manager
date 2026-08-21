"""
Tool execution log model.

Every MCP tool invocation writes one row here (see the logging
decorator added in Phase 4). Used for observability/debugging and for
the "tool_execution_logs" table required by the spec. Never stores
raw request payloads that could contain secrets — only a short,
human-readable input_summary.
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import ToolExecutionStatus


class ToolExecutionLog(Base):
    __tablename__ = "tool_execution_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    tool_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    input_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[ToolExecutionStatus] = mapped_column(nullable=False, index=True)
    execution_time_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )

    user: Mapped["User | None"] = relationship(back_populates="tool_logs")

    def __repr__(self) -> str:
        return f"<ToolExecutionLog tool={self.tool_name!r} status={self.status}>"
