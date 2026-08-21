# REST API Documentation — AI Life Manager

Base URL Prefix: `/api/v1`

All protected endpoints require the HTTP header:
`Authorization: Bearer <access_token>`

---

## 1. Authentication (`/api/v1/auth`)

### `POST /auth/register`
- **Body**: `{"email": "user@example.com", "password": "...", "full_name": "...", "currency_pref": "INR"}`
- **Response**: `201 Created` with User object.

### `POST /auth/login`
- **Body**: `{"email": "user@example.com", "password": "..."}`
- **Response**: `200 OK` with `{"access_token": "...", "refresh_token": "...", "token_type": "bearer", "expires_in": 1800}`.

### `GET /auth/me` *(Protected)*
- **Response**: `200 OK` with user profile.

---

## 2. Expenses (`/api/v1/expenses`)

### `GET /expenses` *(Protected)*
- **Query Params**: `category`, `start_date`, `end_date`, `limit`
- **Response**: List of expenses.

### `POST /expenses` *(Protected)*
- **Body**: `{"amount": 250.0, "category": "Food", "description": "Lunch", "date": "2026-08-21", "payment_method": "upi"}`
- **Response**: `201 Created` with Expense object.

### `DELETE /expenses/{id}` *(Protected)*
- **Response**: `204 No Content`.

---

## 3. Reminders (`/api/v1/reminders`)

### `GET /reminders` *(Protected)*
- **Query Params**: `when` (`all`, `today`, `tomorrow`, `upcoming`, `overdue`), `status`
- **Response**: List of reminders.

### `POST /reminders` *(Protected)*
- **Body**: `{"title": "Assignment", "due_date": "2026-08-22", "due_time": "18:00", "priority": "high", "recurrence": "none"}`
- **Response**: `201 Created`.

### `POST /reminders/{id}/complete` *(Protected)*
- **Response**: `200 OK` with completed reminder and next recurring occurrence if configured.

---

## 4. Budgets (`/api/v1/budgets`)

### `GET /budgets` *(Protected)*
- **Response**: List of evaluated budgets with spent, remaining, and utilization %.

### `POST /budgets` *(Protected)*
- **Body**: `{"amount": 5000.0, "category": "Food", "period": "monthly"}`
- **Response**: `200 OK` with Budget object.

---

## 5. Analytics & Day Planner (`/api/v1/analytics`, `/api/v1/planner`)

### `GET /analytics/comparison` *(Protected)*
- **Response**: Current week vs previous week totals, difference, and percentage change.

### `GET /analytics/breakdown` *(Protected)*
- **Response**: Spending totals and percentages by category.

### `GET /analytics/insights` *(Protected)*
- **Response**: Plain-language AI financial summary and anomaly alerts.

### `GET /planner/day` *(Protected)*
- **Query Params**: `date` (YYYY-MM-DD), `location`
- **Response**: Complete day plan combining reminders, weather, and safe daily spend.

---

## 6. AI Conversational Assistant (`/api/v1/chat`)

### `POST /chat`
- **Body**: `{"message": "I spent 250 on food today", "conversation_history": [...]}`
- **Response**: `{"response": "...", "used_fallback": false, "tools_called": ["add_expense"]}`
