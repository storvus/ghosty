import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import User
from src.utils import hash_password


@pytest_asyncio.fixture
async def user(db_session: AsyncSession):
    payload = {
        "password": "SecurePassword123!",
        "username": "testuser"
    }
    password_hash = hash_password(payload["password"])
    user = User.create(payload["username"], password_hash)
    db_session.add(user)
    await db_session.commit()

    yield user

    await db_session.delete(user)
    await db_session.commit()
