"""
User preferences REST endpoints.
"""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.preference import PreferenceCreateRequest, PreferenceResponse
from app.services.memory_service import MemoryService

router = APIRouter(prefix="/preferences", tags=["preferences"])


@router.get("", response_model=list[PreferenceResponse])
async def list_preferences(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    service = MemoryService(db)
    return await service.list_user_preferences(user_id=current_user.id)


@router.post("", response_model=PreferenceResponse, status_code=status.HTTP_200_OK)
async def save_preference(
    request: PreferenceCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    service = MemoryService(db)
    try:
        return await service.save_user_preference(
            user_id=current_user.id,
            key=request.key,
            value=request.value,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from None


@router.get("/{key}", response_model=dict[str, Any])
async def get_preference(
    key: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    service = MemoryService(db)
    return await service.get_user_preference(user_id=current_user.id, key=key)
