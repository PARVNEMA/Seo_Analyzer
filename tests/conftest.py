"""Main test configuration and fixtures.

Sets up an in-memory async SQLite database, overrides the app's `get_db`
dependency, and provides authenticated HTTP clients.
"""

from __future__ import annotations

import asyncio
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.core.security import create_access_token
from app.crud.user import user_crud
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.user import User
from app.schemas.user import UserCreate

# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

settings = get_settings()

@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for each test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a clean database session for each test.

    Creates all tables before the test and drops them after.
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Provide an unauthenticated test client."""
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest_asyncio.fixture(scope="function")
async def test_user(db_session: AsyncSession) -> User:
    """Create and return a standard user."""
    user_in = UserCreate(
        email="user@example.com",
        password="password123",
        full_name="Test User",
    )
    user = await user_crud.create(db_session, obj_in=user_in)
    return user

@pytest_asyncio.fixture(scope="function")
async def superuser(db_session: AsyncSession) -> User:
    """Create and return a superuser."""
    user_in = UserCreate(
        email="admin@example.com",
        password="adminpassword",
        full_name="Admin User",
    )
    user = await user_crud.create(db_session, obj_in=user_in)
    user.is_superuser = True
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest_asyncio.fixture(scope="function")
async def authenticated_client(client: AsyncClient, test_user: User) -> AsyncClient:
    """Provide a client authenticated as a standard user."""
    token = create_access_token(subject=str(test_user.id))
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client

@pytest_asyncio.fixture(scope="function")
async def superuser_client(client: AsyncClient, superuser: User) -> AsyncClient:
    """Provide a client authenticated as a superuser."""
    token = create_access_token(subject=str(superuser.id))
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client
