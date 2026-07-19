import logging
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.message import Message

logger = logging.getLogger(__name__)


class MessageRepository(Protocol):

    async def get_history(self, conversation_id: int, before_message_id: int, limit: int = 50) -> list[Message]:
        ...

    async def create_message(self, client_message_id: str, sender_id: int, conversation_id: int, text: str) -> Message:
        ...

    async def get_by_client_message_id(self, client_message_id: str, sender_id: int) -> Message | None:
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

    async def get_by_client_message_id(self, client_message_id: str, sender_id: int) -> Message | None:
        query = (
            select(Message)
            .where(Message.client_message_id == client_message_id, Message.sender_id == sender_id)
        )
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()

    async def create_message(self, client_message_id: str, sender_id: int, conversation_id: int, text: str) -> Message:
        message = Message(
            client_message_id=client_message_id,
            sender_id=sender_id,
            conversation_id=conversation_id,
            text=text
        )
        self.db_session.add(message)
        return message
