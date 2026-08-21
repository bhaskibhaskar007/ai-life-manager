"""Repository for the tool_execution_logs table (observability)."""

from app.database import AsyncSessionLocal
from app.models.enums import ToolExecutionStatus
from app.models.tool_log import ToolExecutionLog


async def record_tool_execution(
    *,
    user_id: int | None,
    tool_name: str,
    input_summary: str | None,
    status: ToolExecutionStatus,
    execution_time_ms: float | None,
    error: str | None = None,
) -> None:
    """
    Insert one execution-log row. Uses its own short-lived session so a
    logging failure can never take down the tool call it's logging —
    callers should wrap this in try/except and swallow errors (see
    `app.mcp.logging.log_tool_execution`).
    """
    async with AsyncSessionLocal() as session:
        session.add(
            ToolExecutionLog(
                user_id=user_id,
                tool_name=tool_name,
                input_summary=input_summary,
                status=status,
                execution_time_ms=execution_time_ms,
                error=error,
            )
        )
        await session.commit()
