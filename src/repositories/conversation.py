from typing import Protocol

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from src.dto.chat_response import ChatResponse
from src.dto.message_response import MessageResponse
from src.models import Conversation, ConversationParticipant, Message


class ConversationRepository(Protocol):

    async def get_conversations_for_user_id(self, user_id: int) -> list[ChatResponse]:
        ...

    async def is_participant(self, user_id: int, conversation_id: int) -> bool:
        ...


class SqlAlchemyConversationRepository:

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    async def get_conversations_for_user_id(self, user_id: int) -> list[ChatResponse]:
        LastMessage = aliased(Message)

        unread_count = (
            select(func.count())
            .where(
                Message.conversation_id == ConversationParticipant.conversation_id,
                or_(
                    ConversationParticipant.last_read_message_id == None,
                    Message.id > ConversationParticipant.last_read_message_id,
                )
            )
            .scalar_subquery()
        )

        query = (
            select(
                ConversationParticipant.conversation_id,
                LastMessage.id.label("last_message_id"),
                LastMessage.text.label("last_message_text"),
                LastMessage.sender_id.label("last_message_sender_id"),
                LastMessage.created_at.label("last_message_created_at"),
                unread_count.label("unread_count"),
            )
            .join(
                LastMessage,
                LastMessage.id == (
                    select(Message.id)
                    .where(Message.conversation_id == ConversationParticipant.conversation_id)
                    .order_by(Message.id.desc())
                    .limit(1)
                    .scalar_subquery()
                ),
                isouter=True
            )
            .where(ConversationParticipant.user_id == user_id)
        )
        result = await self.db_session.execute(query)
        conversations = result.mappings().all()
        return [
            ChatResponse(
                conversation_id=conversation["conversation_id"],
                last_message=MessageResponse(
                    id=conversation["last_message_id"],
                    text=conversation["last_message_text"],
                    sender_id=conversation["last_message_sender_id"],
                    created_at=conversation["last_message_created_at"].isoformat()
                ) if conversation["last_message_id"] else None,
                unread_count=conversation["unread_count"]
            )
            for conversation in conversations
        ]

    async def is_participant(self, user_id: int, conversation_id: int) -> bool:
        result = await self.db_session.execute(
            select(ConversationParticipant)
            .where(
                ConversationParticipant.user_id == user_id,
                ConversationParticipant.conversation_id == conversation_id,
                )
        )
        return result.scalar_one_or_none() is not None
