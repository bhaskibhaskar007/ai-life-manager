"""
`@log_tool_execution` — wraps an MCP tool function so that every call
is timed, logged to `tool_execution_logs`, and any exception is turned
into a safe structured error instead of a raw traceback leaking to the
LLM/user.

Usage (inside a tool module):

    from app.mcp.logging import log_tool_execution

    @mcp.tool
    @log_tool_execution("add_expense")
    async def add_expense(user_id: int, amount: float, ...) -> dict:
        ...
"""

from __future__ import annotations

import functools
import time
from collections.abc import Callable
from typing import Any

from app.models.enums import ToolExecutionStatus
from app.repositories.tool_log_repository import record_tool_execution
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Keys that must never be written to the execution log, even truncated.
_SENSITIVE_KEYS = {"password", "password_hash", "token", "access_token", "refresh_token", "jwt_secret_key"}


def _summarize_kwargs(kwargs: dict[str, Any], max_len: int = 200) -> str:
    safe_items = {k: v for k, v in kwargs.items() if k.lower() not in _SENSITIVE_KEYS}
    summary = ", ".join(f"{k}={v!r}" for k, v in safe_items.items())
    return summary[:max_len]


def log_tool_execution(tool_name: str) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.perf_counter()
            user_id = kwargs.get("user_id")
            input_summary = _summarize_kwargs(kwargs)

            try:
                result = await func(*args, **kwargs)
                elapsed_ms = (time.perf_counter() - start) * 1000
                await _safe_log(
                    user_id=user_id,
                    tool_name=tool_name,
                    input_summary=input_summary,
                    status=ToolExecutionStatus.SUCCESS,
                    execution_time_ms=elapsed_ms,
                )
                return result

            except Exception as exc:  # noqa: BLE001 — intentionally broad: this is the tool's safety net
                elapsed_ms = (time.perf_counter() - start) * 1000
                logger.exception("Tool '%s' failed", tool_name)
                await _safe_log(
                    user_id=user_id,
                    tool_name=tool_name,
                    input_summary=input_summary,
                    status=ToolExecutionStatus.ERROR,
                    execution_time_ms=elapsed_ms,
                    error=str(exc)[:500],
                )
                # Return a structured error instead of raising a raw traceback
                # up through the MCP transport — tools should always give the
                # LLM something interpretable to relay back to the user.
                return {
                    "success": False,
                    "error": "Something went wrong while running this tool. Please try again.",
                }

        return wrapper

    return decorator


async def _safe_log(**kwargs: Any) -> None:
    """Logging must never crash the tool call it's observing."""
    try:
        await record_tool_execution(**kwargs)
    except Exception:  # noqa: BLE001
        logger.exception("Failed to write tool execution log")
