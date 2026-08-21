"""
Shared pytest fixtures.

IMPORTANT: environment variables must be set *before* any `app.*`
module is imported, since `app.config.get_settings()` is cached and
`app.database` builds its engine at import time. That's why this file
sets os.environ at module load — pytest always imports conftest.py
before collecting test modules.

Uses a real file-based SQLite DB (not `:memory:`) because `:memory:`
databases are per-connection, and SQLAlchemy's async engine can open
multiple connections from its pool — each would see an empty database.
A temp file is shared correctly across connections and is deleted
after the test session.
"""

import os
import pathlib
import uuid

TEST_DB_PATH = pathlib.Path(__file__).parent / "test_ai_life_manager.db"
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-not-for-production-use")
os.environ.setdefault("DATABASE_URL", f"sqlite+aiosqlite:///{TEST_DB_PATH}")

import pytest_asyncio  # noqa: E402

from app.database import AsyncSessionLocal, Base, engine  # noqa: E402
from app.models.user import User  # noqa: E402
from app.utils.seed_categories import seed_default_categories  # noqa: E402


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await seed_default_categories()

    yield

    await engine.dispose()
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()


@pytest_asyncio.fixture
async def test_user_id() -> int:
    """Creates a fresh throwaway user for a single test and returns its id."""
    async with AsyncSessionLocal() as session:
        user = User(
            email=f"test-{uuid.uuid4()}@example.com",
            password_hash="not-a-real-hash",
            currency_pref="INR",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user.id
