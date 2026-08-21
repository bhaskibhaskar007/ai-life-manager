"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-08-09

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("currency_pref", sa.String(3), nullable=False, server_default="INR"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "expense_categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("is_custom", sa.Boolean(), nullable=False, server_default="0"),
    )

    op.create_table(
        "expenses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("expense_categories.id"), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("description", sa.String(255), nullable=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column(
            "payment_method",
            sa.Enum("cash", "card", "upi", "net_banking", "wallet", "other", name="paymentmethod"),
            nullable=False,
            server_default="other",
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_expenses_user_id", "expenses", ["user_id"])
    op.create_index("ix_expenses_date", "expenses", ["date"])

    op.create_table(
        "budgets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("expense_categories.id"), nullable=True),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column(
            "period",
            sa.Enum("weekly", "monthly", "yearly", name="budgetperiod"),
            nullable=False,
            server_default="monthly",
        ),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_budgets_user_id", "budgets", ["user_id"])

    op.create_table(
        "reminders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("due_time", sa.Time(), nullable=True),
        sa.Column(
            "priority",
            sa.Enum("low", "medium", "high", name="reminderpriority"),
            nullable=False,
            server_default="medium",
        ),
        sa.Column(
            "status",
            sa.Enum("pending", "completed", "overdue", "cancelled", name="reminderstatus"),
            nullable=False,
            server_default="pending",
        ),
        sa.Column(
            "recurrence",
            sa.Enum("none", "daily", "weekly", "monthly", name="recurrencetype"),
            nullable=False,
            server_default="none",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_reminders_user_id", "reminders", ["user_id"])
    op.create_index("ix_reminders_due_date", "reminders", ["due_date"])
    op.create_index("ix_reminders_status", "reminders", ["status"])

    op.create_table(
        "user_preferences",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("key", sa.String(100), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        # Defined inline (not as a separate op.create_unique_constraint
        # call) because SQLite cannot ALTER a table to add a constraint
        # after creation — only Postgres/MySQL support that. Declaring it
        # as part of create_table works on every dialect.
        sa.UniqueConstraint("user_id", "key", name="uq_user_preference_key"),
    )
    op.create_index("ix_user_preferences_user_id", "user_preferences", ["user_id"])

    op.create_table(
        "conversation_context",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("embedding", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_conversation_context_user_id", "conversation_context", ["user_id"])
    op.create_index("ix_conversation_context_created_at", "conversation_context", ["created_at"])

    op.create_table(
        "tool_execution_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("tool_name", sa.String(100), nullable=False),
        sa.Column("input_summary", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("success", "error", name="toolexecutionstatus"),
            nullable=False,
        ),
        sa.Column("execution_time_ms", sa.Float(), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_tool_execution_logs_user_id", "tool_execution_logs", ["user_id"])
    op.create_index("ix_tool_execution_logs_tool_name", "tool_execution_logs", ["tool_name"])
    op.create_index("ix_tool_execution_logs_status", "tool_execution_logs", ["status"])
    op.create_index("ix_tool_execution_logs_created_at", "tool_execution_logs", ["created_at"])


def downgrade() -> None:
    op.drop_table("tool_execution_logs")
    op.drop_table("conversation_context")
    op.drop_table("user_preferences")
    op.drop_table("reminders")
    op.drop_table("budgets")
    op.drop_table("expenses")
    op.drop_table("expense_categories")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

    # Drop enum types explicitly (Postgres does not auto-drop them with the table)
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        for enum_name in (
            "paymentmethod",
            "budgetperiod",
            "reminderpriority",
            "reminderstatus",
            "recurrencetype",
            "toolexecutionstatus",
        ):
            sa.Enum(name=enum_name).drop(bind, checkfirst=True)
