"""Budget model — overall or per-category, weekly/monthly/yearly."""

import datetime as dt
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import BudgetPeriod


class Budget(Base):
    __tablename__ = "budgets"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    # NULL category_id = an overall budget across all categories
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("expense_categories.id"), nullable=True
    )

    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    period: Mapped[BudgetPeriod] = mapped_column(default=BudgetPeriod.MONTHLY, server_default=BudgetPeriod.MONTHLY.value)
    start_date: Mapped[dt.date] = mapped_column(Date, nullable=False)

    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: dt.datetime.now(dt.timezone.utc)
    )

    user: Mapped["User"] = relationship(back_populates="budgets")
    category: Mapped["ExpenseCategory | None"] = relationship()

    def __repr__(self) -> str:
        return f"<Budget id={self.id} amount={self.amount} period={self.period}>"
