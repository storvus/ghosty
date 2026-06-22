import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import User
from src.tests.factories import UserFactory
from src.utils import create_token, hash_password

# login tests hardcode this password, keep it stable
_USER_PASSWORD = "SecurePassword123!"


@pytest_asyncio.fixture
async def user(db_session: AsyncSession):
    u = UserFactory.build(username="testuser", password_hash=hash_password(_USER_PASSWORD))
    db_session.add(u)
    await db_session.commit()
    yield u


@pytest.fixture
def auth_headers(user: User) -> dict:
    return {"Authorization": f"Bearer {create_token(user.id)}"}
