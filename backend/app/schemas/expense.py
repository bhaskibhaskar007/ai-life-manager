"""Expense schemas."""

from datetime import date
from decimal import Decimal
from pydantic import BaseModel, Field


class ExpenseCreateRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Amount spent")
    category: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=255)
    expense_date: str | None = Field(None, alias="date", description="YYYY-MM-DD")
    payment_method: str = Field("other", description="cash, card, upi, net_banking, wallet, other")
    notes: str | None = None


class ExpenseUpdateRequest(BaseModel):
    amount: float | None = Field(None, gt=0)
    category: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=255)
    expense_date: str | None = Field(None, alias="date")
    payment_method: str | None = None
    notes: str | None = None


class ExpenseResponse(BaseModel):
    id: int
    amount: float
    category: str
    description: str | None
    date: str
    payment_method: str
    notes: str | None


class CategoryResponse(BaseModel):
    id: int
    name: str
    is_custom: bool
