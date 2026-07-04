from collections.abc import Callable, Coroutine

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Conversation, ConversationParticipant, Message, User
from src.tests.factories import ConversationFactory, MessageFactory


@pytest_asyncio.fixture
async def make_conversation(db_session: AsyncSession) -> Callable[..., Coroutine]:
    """
    Factory fixture — call it to create a persisted Conversation with participants.
    conv = await make_conversation(user, other_user)
    """
    async def _build(*participants: User) -> Conversation:
        conv = ConversationFactory.build()
        db_session.add(conv)
        await db_session.flush()
        for p in participants:
            db_session.add(ConversationParticipant(conversation_id=conv.id, user_id=p.id))
        return conv

    yield _build


@pytest_asyncio.fixture
async def make_message(db_session: AsyncSession) -> Callable[..., Coroutine]:
    """
    Factory fixture — call it to create a persisted Message for a user and a conversation.
    msg = await make_message(user, conversation)
    """
    async def _build(user: User, conv: Conversation) -> Message:
        msg = MessageFactory.build(sender_id=user.id, conversation_id=conv.id)
        db_session.add(msg)
        await db_session.flush()
        return msg

    yield _build
