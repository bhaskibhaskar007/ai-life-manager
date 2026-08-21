"""
Day Planner REST endpoint.
"""

from typing import Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.services.planner_service import PlannerService
from app.utils.parsing import parse_iso_date

router = APIRouter(prefix="/planner", tags=["planner"])


@router.get("/day")
async def get_day_plan(
    date_str: str | None = Query(None, alias="date", description="YYYY-MM-DD"),
    location: str = Query("Bengaluru", description="City location for weather forecast"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    service = PlannerService(db)
    target_date = parse_iso_date(date_str) if date_str else None
    return await service.generate_day_plan(user_id=current_user.id, target_date=target_date, location=location)
