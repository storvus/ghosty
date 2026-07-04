from collections.abc import Callable, Coroutine

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_session
from src.main import app
from src.models import User
from src.tests.factories import UserFactory
from src.utils import create_token


@pytest_asyncio.fixture
async def async_client(db_session: AsyncSession):
    """Create an async client for testing."""
    app.dependency_overrides[get_session] = lambda: db_session
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def build_user(db_session: AsyncSession) -> Callable[..., Coroutine]:
    """
    Factory fixture — call it to create a persisted User.

        user3 = await build_user()
        user4 = await build_user(username="custom")
    """
    async def _build(**kwargs) -> User:
        u = UserFactory.build(**kwargs)
        db_session.add(u)
        await db_session.flush()
        return u

    yield _build


@pytest_asyncio.fixture
async def user(build_user) -> User:
    return await build_user()


@pytest.fixture
def auth_headers(user: User) -> dict:
    return {"Authorization": f"Bearer {create_token(user.id)}"}
