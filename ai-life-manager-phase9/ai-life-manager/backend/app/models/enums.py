"""
Shared enums used by multiple ORM models.

Using Python `enum.Enum` + SQLAlchemy `Enum` gives us DB-level constraints
(invalid values are rejected at the database, not just in application code)
while still getting type-safe values in Python.
"""

import enum


class PaymentMethod(str, enum.Enum):
    CASH = "cash"
    CARD = "card"
    UPI = "upi"
    NET_BANKING = "net_banking"
    WALLET = "wallet"
    OTHER = "other"


class ReminderPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ReminderStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class RecurrenceType(str, enum.Enum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class BudgetPeriod(str, enum.Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class ToolExecutionStatus(str, enum.Enum):
    SUCCESS = "success"
    ERROR = "error"
