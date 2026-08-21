"""
Reminders REST endpoints.
"""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.enums import RecurrenceType, ReminderPriority, ReminderStatus
from app.models.user import User
from app.schemas.reminder import (
    ReminderCreateRequest,
    ReminderResponse,
    ReminderUpdateRequest,
)
from app.services.reminder_service import ReminderService
from app.utils.parsing import parse_iso_date, parse_iso_time

router = APIRouter(prefix="/reminders", tags=["reminders"])


@router.post("", response_model=ReminderResponse, status_code=status.HTTP_201_CREATED)
async def create_reminder(
    request: ReminderCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    service = ReminderService(db)
    due_date = parse_iso_date(request.due_date)
    if not due_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid due_date format (use YYYY-MM-DD).")
    due_time = parse_iso_time(request.due_time) if request.due_time else None

    try:
        priority_enum = ReminderPriority(request.priority.lower())
    except ValueError:
        priority_enum = ReminderPriority.MEDIUM

    try:
        recurrence_enum = RecurrenceType(request.recurrence.lower())
    except ValueError:
        recurrence_enum = RecurrenceType.NONE

    try:
        return await service.create_reminder(
            user_id=current_user.id,
            title=request.title,
            due_date=due_date,
            description=request.description,
            due_time=due_time,
            priority=priority_enum,
            recurrence=recurrence_enum,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from None


@router.get("", response_model=list[ReminderResponse])
async def list_reminders(
    when: str = Query("all", description="all, today, tomorrow, upcoming, overdue"),
    status_filter: str | None = Query(None, alias="status", description="pending, completed, overdue, cancelled"),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    service = ReminderService(db)
    status_enum = None
    if status_filter:
        try:
            status_enum = ReminderStatus(status_filter.lower())
        except ValueError:
            pass

    try:
        return await service.list_reminders(
            user_id=current_user.id,
            when=when,
            status=status_enum,
            limit=limit,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from None


@router.put("/{reminder_id}", response_model=ReminderResponse)
async def update_reminder(
    reminder_id: int,
    request: ReminderUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    service = ReminderService(db)
    due_date = parse_iso_date(request.due_date) if request.due_date else None
    due_time = parse_iso_time(request.due_time) if request.due_time else None
    priority_enum = None
    if request.priority:
        try:
            priority_enum = ReminderPriority(request.priority.lower())
        except ValueError:
            pass
    recurrence_enum = None
    if request.recurrence:
        try:
            recurrence_enum = RecurrenceType(request.recurrence.lower())
        except ValueError:
            pass

    try:
        updated = await service.update_reminder(
            user_id=current_user.id,
            reminder_id=reminder_id,
            title=request.title,
            description=request.description,
            due_date=due_date,
            due_time=due_time,
            priority=priority_enum,
            recurrence=recurrence_enum,
        )
        if not updated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found.")
        return updated
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from None


@router.post("/{reminder_id}/complete")
async def complete_reminder(
    reminder_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    service = ReminderService(db)
    result = await service.complete_reminder(user_id=current_user.id, reminder_id=reminder_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found.")
    return result


@router.delete("/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reminder(
    reminder_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    service = ReminderService(db)
    deleted = await service.delete_reminder(user_id=current_user.id, reminder_id=reminder_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found.")
