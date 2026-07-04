from typing import Protocol

from sqlalchemy import select, case, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import User


class UserRepository(Protocol):

    async def search_users(self, username: str) -> list[User]:
        ...

    async def get_user_by_id(self, user_id: int) -> User | None:
        ...

    async def get_user_by_ids(self, user_ids: list[int]) -> list[User]:
        ...

    async def get_user_by_username(self, username: str) -> User | None:
        ...

    def add(self, user: User):
        ...


class SqlAlchemyUserRepository:

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def search_users(self, search_string: str, limit=20) -> list[User]:
        query = (
            select(User)
            .where(
                # ToDo: add search by display_number
                User.username.ilike(f"%{search_string}%"),
            )
            .order_by(
                case(
                    (User.username == search_string, 0),
                    (User.username.ilike(f"{search_string}%"), 1),
                    else_=2
                )
            )
            .limit(limit)
        )
        users = await self.db_session.execute(query)
        return list(users.scalars())

    async def get_user_by_ids(self, user_ids: list[int]) -> list[User]:
        query = select(User).where(User.id.in_(user_ids))
        users = await self.db_session.execute(query)
        return list(users.scalars())

    async def get_user_by_id(self, user_id: int) -> User | None:
        query = select(User).where(User.id == user_id)
        user = await self.db_session.execute(query)
        return user.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        query = select(User).where(User.username == username)
        user = await self.db_session.execute(query)
        return user.scalar_one_or_none()

    def add(self, user: User):
        self.db_session.add(user)
