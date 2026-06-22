from collections.abc import Callable, Coroutine

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Conversation, ConversationParticipant, Message, User
from src.tests.factories import ConversationFactory, UserFactory, MessageFactory
from src.utils import create_token


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
