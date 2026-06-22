import logging
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.message import Message

logger = logging.getLogger(__name__)


class MessageRepository(Protocol):

    async def get_history(self, conversation_id: int, before_message_id: int, limit: int = 50) -> list[Message]:
        ...

class SqlAlchemyMessageRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_history(self, conversation_id: int, before_message_id: int, limit: int = 50) -> list[Message]:
        query = (
            select(Message)
            .where(Message.conversation_id == conversation_id, Message.id < before_message_id)
            .order_by(Message.id.desc())
            .limit(limit)
        )
        result = await self.db_session.execute(query)
        return result.scalars().all()
