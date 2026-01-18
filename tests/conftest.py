"""Pytest configuration and shared fixtures"""
import asyncio
import pytest
import uuid
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import Base, get_db
from app.config import settings

# Use existing database for tests (will use transactions and rollback)
# Note: auth.users table is managed by Supabase and already exists
test_engine = create_async_engine(settings.DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Note: We don't create auth.users table - it's managed by Supabase
# Foreign keys to auth.users will work automatically since the table already exists

@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Create database session for each test.

    Uses transaction rollback to ensure test isolation without affecting database.
    """
    async with TestSessionLocal() as session:
        # Start a transaction
        transaction = await session.begin()

        # Override commit to use flush instead (don't commit in tests)
        async def fake_commit():
            await session.flush()

        session.commit = fake_commit

        yield session

        # Rollback transaction after test (automatic cleanup)
        await transaction.rollback()
        await session.close()

@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    HTTP client for testing API endpoints.

    Overrides get_db dependency to use test database.
    """
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", follow_redirects=True) as ac:
        yield ac

    app.dependency_overrides.clear()

@pytest.fixture
async def test_user_id() -> uuid.UUID:
    """Get a fixed UUID for test user"""
    return uuid.UUID("3f3f3f3f-3f3f-3f3f-3f3f-3f3f3f3f3f3f")

@pytest.fixture
async def auth_headers(client: AsyncClient, test_user_id: str) -> dict:
    """
    Create test user and return auth headers.

    Usage:
        async def test_protected_endpoint(client, auth_headers):
            response = await client.get("/api/fields", headers=auth_headers)
    """
    # Register user
    register_data = {
        "email": "test@example.com",
        "password": "TestPassword123",
        "full_name": "Test User"
    }
    await client.post("/api/auth/register", json=register_data)

    # Login
    login_data = {
        "username": "test@example.com",
        "password": "TestPassword123"
    }
    response = await client.post("/api/auth/login", data=login_data)
    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}
