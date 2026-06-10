from typing import Protocol

from sqlalchemy import select, case
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import User


class UserRepository(Protocol):

    async def search_users(self, username: str) -> list[User]:
        ...

    async def get_user_by_id(self, user_id: int) -> User | None:
        ...

    async def get_user_by_username(self, username: str) -> User | None:
        ...

    def add(self, user: User):
        ...


class SqlAlchemyUserRepository:

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def search_users(self, username: str, limit=20) -> list[User]:
        query = (
            select(User)
            .where(User.username.ilike(f"%{username}%"))
            .order_by(
                case(
                    (User.username == username, 0),
                    (User.username.ilike(f"{username}%"), 1),
                    else_=2
                )
            )
            .limit(limit)
        )
        result = await self.db_session.execute(query)
        return list(result.scalars())

    async def get_user_by_id(self, user_id: int) -> User | None:
        query = select(User).where(User.id == user_id)
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        query = select(User).where(User.username == username)
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()

    def add(self, user: User):
        self.db_session.add(user)
