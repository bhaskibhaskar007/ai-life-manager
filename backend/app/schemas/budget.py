"""Budget schemas."""

from pydantic import BaseModel, Field


class BudgetCreateRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Budget amount")
    category: str | None = Field(None, description="Category name (None for overall budget)")
    period: str = Field("monthly", description="weekly, monthly, yearly")


class BudgetResponse(BaseModel):
    id: int
    category: str | None
    amount: float
    period: str
    start_date: str
    spent: float | None = None
    remaining: float | None = None
    percentage_used: float | None = None
    status: str | None = None
    was_updated: bool | None = None
