"""
Day Planner MCP tools.

Provides automated schedule planning grounded in the user's actual
pending reminders, weather forecasts, and monthly budget limits.
"""

from app.database import AsyncSessionLocal
from app.mcp.logging import log_tool_execution
from app.mcp.server import mcp
from app.services.planner_service import PlannerService
from app.utils.parsing import parse_iso_date


@mcp.tool
@log_tool_execution("plan_day")
async def plan_day(
    user_id: int,
    target_date: str | None = None,
    location: str | None = "Bengaluru",
) -> dict:
    """
    Generates a structured daily plan for `target_date` (YYYY-MM-DD,
    defaults to today). Reads the user's active reminders, weather
    forecast, and daily budget limits to construct morning, afternoon,
    and evening schedule blocks.
    """
    async with AsyncSessionLocal() as session:
        service = PlannerService(session)
        parsed_date = parse_iso_date(target_date) if target_date else None
        result = await service.generate_day_plan(
            user_id=user_id,
            target_date=parsed_date,
            location=location or "Bengaluru",
        )
        return {"success": True, "plan": result}
