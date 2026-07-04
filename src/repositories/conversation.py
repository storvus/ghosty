from typing import Protocol

from sqlalchemy import select, func, or_, true
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from src.dto.chat_response import ConversationRow
from src.dto.message_response import MessageResponse
from src.models import Conversation, ConversationParticipant, Message


class ConversationRepository(Protocol):

    async def get_conversations_for_user_id(self, user_id: int) -> list[ConversationRow]:
        ...

    async def is_participant(self, user_id: int, conversation_id: int) -> bool:
        ...


class SqlAlchemyConversationRepository:

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    async def get_conversations_for_user_id(self, user_id: int) -> list[ConversationRow]:
        Companions = aliased(ConversationParticipant)

        unread = (
            select(
                func.count().label("unread_count")
            )
            .select_from(Message)
            .where(
                Message.conversation_id == ConversationParticipant.conversation_id,
                or_(
                    ConversationParticipant.last_read_message_id.is_(None),
                    Message.id > ConversationParticipant.last_read_message_id,
                )
            )
            .correlate(ConversationParticipant)
        ).lateral().alias("unread")

        last_message = (
            select(
                Message.id,
                Message.text,
                Message.sender_id,
                Message.created_at
            )
            .where(Message.conversation_id == ConversationParticipant.conversation_id)
            .order_by(Message.id.desc())
            .limit(1)
            .correlate(ConversationParticipant)
        ).lateral().alias("last_message")

        participants = (
            select(
                func.json_agg(Companions.user_id).label("participant_ids")
            )
            .where(Companions.conversation_id == ConversationParticipant.conversation_id)
            .correlate(ConversationParticipant)
        ).lateral().alias("participants")

        query = (
            select(
                Conversation.type,
                ConversationParticipant.conversation_id,
                ConversationParticipant.last_read_message_id,
                last_message.c.id.label("last_message_id"),
                last_message.c.text.label("last_message_text"),
                last_message.c.sender_id.label("last_message_sender_id"),
                last_message.c.created_at.label("last_message_created_at"),
                unread.c.unread_count,
                participants.c.participant_ids,
            )
            .select_from(ConversationParticipant)
            .join(Conversation, Conversation.id == ConversationParticipant.conversation_id)
            .join(last_message, true(), isouter=True)
            .join(unread, true(), isouter=True)
            .join(participants, true(), isouter=True)
            .where(ConversationParticipant.user_id == user_id)
        )
        result = await self.db_session.execute(query)
        conversations = result.mappings().all()
        return [
            ConversationRow(
                conversation_id=conversation["conversation_id"],
                last_read_message_id=conversation["last_read_message_id"],
                type=conversation["type"],
                participant_ids=conversation["participant_ids"],
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
