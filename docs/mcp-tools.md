# FastMCP Tool Registry & Documentation

This document specifies all 8 FastMCP tool groups registered on the `FastMCP` server instance in `app.mcp.server`.

---

## 1. Expense Tools (`app/mcp/tools/expense.py`)

| Tool Name | Parameters | Return Type | Description |
| :--- | :--- | :--- | :--- |
| `add_expense` | `user_id: int, amount: float, category: str, description: str?, expense_date: str?, payment_method: str?, notes: str?` | `dict` | Records a validated expense transaction. |
| `get_expenses` | `user_id: int, category: str?, start_date: str?, end_date: str?, limit: int` | `dict` | Lists transactions filtered by category/date range. |
| `update_expense` | `user_id: int, expense_id: int, amount: float?, category: str?, description: str?, expense_date: str?, payment_method: str?, notes: str?` | `dict` | Updates an existing expense record. |
| `delete_expense` | `user_id: int, expense_id: int` | `dict` | Permanently deletes an expense record. |
| `get_expense_summary` | `user_id: int, start_date: str, end_date: str` | `dict` | Returns total spent, count, and daily average. |
| `get_category_breakdown`| `user_id: int, start_date: str, end_date: str` | `dict` | Returns category percentage breakdown & top category. |
| `compare_weekly_expenses`| `user_id: int, reference_date: str?` | `dict` | Compares current week spending with previous week. |
| `get_spending_trend` | `user_id: int, weeks: int` | `dict` | Evaluates spending trajectory (increasing/decreasing/stable). |

---

## 2. Analytics Tools (`app/mcp/tools/analytics.py`)

| Tool Name | Parameters | Return Type | Description |
| :--- | :--- | :--- | :--- |
| `calculate_weekly_total` | `user_id: int, reference_date: str?` | `dict` | Computes aggregate spending for a calendar week. |
| `calculate_previous_week_total` | `user_id: int, reference_date: str?` | `dict` | Computes spending for the immediately preceding week. |
| `calculate_percentage_change` | `current_amount: float, previous_amount: float` | `dict` | Pure mathematical change calculator; safely handles `0` previous amount. |
| `detect_spending_trend` | `user_id: int, weeks: int` | `dict` | Multi-week trend analyzer. |
| `detect_unusual_expense` | `user_id: int, lookback_days: int, threshold_multiplier: float` | `dict` | Flags expenses exceeding category average by multiplier (default 2.5x). |
| `generate_financial_insight`| `user_id: int` | `dict` | Plain-language synthesis of weekly change, top category, and anomalies. |

---

## 3. Reminder Tools (`app/mcp/tools/reminder.py`)

| Tool Name | Parameters | Return Type | Description |
| :--- | :--- | :--- | :--- |
| `create_reminder` | `user_id: int, title: str, due_date: str, due_time: str?, description: str?, priority: str, recurrence: str` | `dict` | Schedules a task with priority and recurrence. |
| `list_reminders` | `user_id: int, when: str, status: str?, limit: int` | `dict` | Queries reminders (`all`, `today`, `tomorrow`, `upcoming`, `overdue`). |
| `update_reminder` | `user_id: int, reminder_id: int, ...` | `dict` | Updates reminder attributes. |
| `complete_reminder` | `user_id: int, reminder_id: int` | `dict` | Marks reminder completed; schedules next occurrence if recurring. |
| `delete_reminder` | `user_id: int, reminder_id: int` | `dict` | Removes a reminder. |

---

## 4. Budget Tools (`app/mcp/tools/budget.py`)

| Tool Name | Parameters | Return Type | Description |
| :--- | :--- | :--- | :--- |
| `create_budget` | `user_id: int, amount: float, category: str?, period: str` | `dict` | Creates/updates an overall or category budget cap. |
| `get_budget` | `user_id: int, category: str?` | `dict` | Retrieves budget configuration. |
| `calculate_remaining_budget`| `user_id: int, category: str?` | `dict` | Calculates spent vs remaining amount and utilization percentage. |
| `detect_budget_risk` | `user_id: int, threshold_percent: float` | `dict` | Identifies budgets exceeding threshold (default 80%). |

---

## 5. Day Planner Tool (`app/mcp/tools/planner.py`)

| Tool Name | Parameters | Return Type | Description |
| :--- | :--- | :--- | :--- |
| `plan_day` | `user_id: int, target_date: str?, location: str?` | `dict` | Synthesizes an organized daily plan with morning, afternoon, and evening blocks based on active reminders, live weather, and safe spending limits. |

---

## 6. Weather Tools (`app/mcp/tools/weather.py`)

| Tool Name | Parameters | Return Type | Description |
| :--- | :--- | :--- | :--- |
| `get_current_weather` | `location: str, user_id: int?` | `dict` | Fetches real-time temperature, condition description, and rain status via Open-Meteo API. |
| `get_forecast` | `location: str, days: int, user_id: int?` | `dict` | Fetches 1-16 day daily weather forecast. |

---

## 7. Memory Tools (`app/mcp/tools/memory.py`)

| Tool Name | Parameters | Return Type | Description |
| :--- | :--- | :--- | :--- |
| `save_user_preference` | `user_id: int, key: str, value: str` | `dict` | Validates key against allow-list and stores preference. |
| `get_user_preference` | `user_id: int, key: str` | `dict` | Retrieves stored preference. |
| `save_user_context` | `user_id: int, summary: str` | `dict` | Persists conversation context summary. |
| `retrieve_relevant_context` | `user_id: int, query: str?, limit: int` | `dict` | Retrieves contextual history for multi-turn awareness. |
