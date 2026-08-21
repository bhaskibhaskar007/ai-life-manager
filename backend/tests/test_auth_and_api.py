"""
Integration tests for Authentication and REST API endpoints.
"""

from httpx import ASGITransport, AsyncClient
import pytest

from app.main import app


@pytest.mark.asyncio
async def test_auth_registration_and_login():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Register new user
        reg_payload = {
            "email": "student_test@example.com",
            "password": "SecurePassword123!",
            "full_name": "Test Student",
            "currency_pref": "INR",
        }
        res = await client.post("/api/v1/auth/register", json=reg_payload)
        assert res.status_code == 201
        data = res.json()
        assert data["email"] == "student_test@example.com"
        assert data["full_name"] == "Test Student"

        # 2. Duplicate registration should fail with 400
        res_dup = await client.post("/api/v1/auth/register", json=reg_payload)
        assert res_dup.status_code == 400

        # 3. Login with invalid password
        res_fail = await client.post(
            "/api/v1/auth/login",
            json={"email": "student_test@example.com", "password": "WrongPassword"},
        )
        assert res_fail.status_code == 401

        # 4. Login with valid password
        res_login = await client.post(
            "/api/v1/auth/login",
            json={"email": "student_test@example.com", "password": "SecurePassword123!"},
        )
        assert res_login.status_code == 200
        tokens = res_login.json()
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        token = tokens["access_token"]

        # 5. Access protected /me endpoint
        headers = {"Authorization": f"Bearer {token}"}
        res_me = await client.get("/api/v1/auth/me", headers=headers)
        assert res_me.status_code == 200
        assert res_me.json()["email"] == "student_test@example.com"


@pytest.mark.asyncio
async def test_protected_expenses_crud():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register & login
        email = "expenses_user@example.com"
        await client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "Password123!", "full_name": "Expense Tester"},
        )
        login_res = await client.post("/api/v1/auth/login", json={"email": email, "password": "Password123!"})
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create expense
        exp_payload = {
            "amount": 350.0,
            "category": "Food",
            "description": "Lunch with team",
            "date": "2026-08-21",
            "payment_method": "upi",
        }
        res_create = await client.post("/api/v1/expenses", json=exp_payload, headers=headers)
        assert res_create.status_code == 201
        created = res_create.json()
        exp_id = created["id"]
        assert created["amount"] == 350.0

        # List expenses
        res_list = await client.get("/api/v1/expenses", headers=headers)
        assert res_list.status_code == 200
        assert len(res_list.json()) >= 1

        # Delete expense
        res_del = await client.delete(f"/api/v1/expenses/{exp_id}", headers=headers)
        assert res_del.status_code == 204


@pytest.mark.asyncio
async def test_protected_reminders_and_planner():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        email = "reminders_user@example.com"
        await client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "Password123!", "full_name": "Reminder Tester"},
        )
        login_res = await client.post("/api/v1/auth/login", json={"email": email, "password": "Password123!"})
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create reminder
        rem_payload = {
            "title": "Submit Assignment",
            "due_date": "2026-08-22",
            "due_time": "18:00",
            "priority": "high",
        }
        res_rem = await client.post("/api/v1/reminders", json=rem_payload, headers=headers)
        assert res_rem.status_code == 201
        rem_id = res_rem.json()["id"]

        # List reminders
        res_list = await client.get("/api/v1/reminders?when=all", headers=headers)
        assert res_list.status_code == 200
        assert len(res_list.json()) >= 1

        # Complete reminder
        res_comp = await client.post(f"/api/v1/reminders/{rem_id}/complete", headers=headers)
        assert res_comp.status_code == 200

        # Get day plan
        res_plan = await client.get("/api/v1/planner/day?date=2026-08-22", headers=headers)
        assert res_plan.status_code == 200
        assert "schedule_blocks" in res_plan.json()


@pytest.mark.asyncio
async def test_chat_api_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.post("/api/v1/chat", json={"message": "how much did I spend this week?"})
        assert res.status_code == 200
        data = res.json()
        assert "response" in data
        assert "tools_called" in data
