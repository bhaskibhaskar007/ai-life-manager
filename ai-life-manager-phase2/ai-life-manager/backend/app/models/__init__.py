"""
Import every ORM model here.

Alembic's `env.py` imports `Base` from `app.database` and relies on
`Base.metadata` already knowing about all tables — which only happens
if every model module has been imported somewhere. This file is that
"somewhere". If you add a new model file, add its import here too.
"""

from app.models.budget import Budget
from app.models.context import ConversationContext
from app.models.expense import Expense, ExpenseCategory
from app.models.preference import UserPreference
from app.models.reminder import Reminder
from app.models.tool_log import ToolExecutionLog
from app.models.user import User

__all__ = [
    "User",
    "Expense",
    "ExpenseCategory",
    "Budget",
    "Reminder",
    "UserPreference",
    "ConversationContext",
    "ToolExecutionLog",
]
