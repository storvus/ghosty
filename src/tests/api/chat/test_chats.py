from datetime import datetime, timedelta, timezone

import jwt
import pytest
from hamcrest import assert_that, contains_inanyorder
from httpx import AsyncClient
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.models import Conversation, ConversationParticipant, User, Message
from src.tests.factories import MessageFactory
from src.utils import create_token

URL = "/api/chats"


async def _set_last_read_message(db_session: AsyncSession, user: User, conv: Conversation, msg: Message):
    await db_session.execute(
        update(ConversationParticipant)
        .where(ConversationParticipant.conversation_id == conv.id, ConversationParticipant.user_id == user.id)
        .values(last_read_message_id=msg.id)
    )
    await db_session.commit()

# ---------------------------------------------------------------------------
# Auth errors
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_chats_no_auth_header(async_client: AsyncClient):
    response = await async_client.get(URL)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_chats_invalid_token(async_client: AsyncClient):
    response = await async_client.get(URL, headers={"Authorization": "Bearer not.a.valid.token"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"


@pytest.mark.asyncio
async def test_get_chats_expired_token(async_client: AsyncClient, user: User):
    payload = {"user_id": user.id, "exp": datetime.now(timezone.utc) - timedelta(seconds=1)}
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.TOKEN_ENCODE_ALGORITHM)
    response = await async_client.get(URL, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Token expired"


@pytest.mark.asyncio
async def test_get_chats_token_for_nonexistent_user(async_client: AsyncClient):
    token = create_token(999_999_999)
    response = await async_client.get(URL, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert response.json()["detail"] == "User not found"


@pytest.mark.asyncio
async def test_get_chats_returns_empty_list_when_no_conversations(async_client: AsyncClient, auth_headers: dict):
    response = await async_client.get(URL, headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_chats_conversation_with_no_messages(
    async_client: AsyncClient,
    auth_headers: dict,
    user: User,
    build_user,
    make_conversation,
):
    other_user = await build_user()
    conv = await make_conversation(user, other_user)

    response = await async_client.get(URL, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data == [
        {
            "conversation_id": conv.id,
            "last_message": None,
            "unread_count": 0
        }
    ]


@pytest.mark.asyncio
async def test_get_chats_last_message_is_most_recent(
    async_client: AsyncClient,
    db_session: AsyncSession,
    auth_headers: dict,
    user: User,
    build_user,
    make_conversation,
):
    other_user = await build_user()
    conv = await make_conversation(user, other_user)
    msg1 = MessageFactory.build(
        sender_id=user.id,
        conversation_id=conv.id,
        text="first",
        created_at=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
    )
    msg2 = MessageFactory.build(
        sender_id=user.id,
        conversation_id=conv.id,
        text="latest",
        created_at=datetime(2024, 1, 1, 12, 0, 1, tzinfo=timezone.utc),
    )
    db_session.add(msg1)
    db_session.add(msg2)
    await db_session.commit()

    response = await async_client.get(URL, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data == [
        {
            "conversation_id": conv.id,
            "last_message": {
                "id": msg2.id,
                "text": msg2.text,
                "sender_id": user.id,
                "created_at": msg2.created_at.isoformat(),
            },
            "unread_count": 2
        }
    ]


@pytest.mark.asyncio
async def test_get_chats_user_only_sees_own_conversations(
    db_session: AsyncSession,
    async_client: AsyncClient,
    auth_headers: dict,
    user: User,
    build_user,
    make_conversation,
    make_message,
):
    user2 = await build_user()
    user3 = await build_user()
    user4 = await build_user()
    user5 = await build_user()

    # all messages read
    shared_conv1 = await make_conversation(user, user2)
    shared_conv1_msg = await make_message(user2, shared_conv1)
    await _set_last_read_message(db_session, user, shared_conv1, shared_conv1_msg)

    # partial read
    shared_conv2 = await make_conversation(user, user3)
    shared_conv2_msg = await make_message(user, shared_conv2)
    shared_conv2_msg2 = await make_message(user3, shared_conv2)
    await _set_last_read_message(db_session, user, shared_conv2, shared_conv2_msg)

    # never read
    shared_conv3 = await make_conversation(user, user4)
    shared_conv3_msg = await make_message(user, shared_conv3)

    # user is not a participant
    await make_conversation(user2, user5)
    await make_conversation(user3, user5)
    await make_conversation(user4, user5)

    response = await async_client.get(URL, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert_that(
        data,
        contains_inanyorder(
            {
                "conversation_id": shared_conv1.id,
                "last_message": {
                    "id": shared_conv1_msg.id,
                    "text": shared_conv1_msg.text,
                    "sender_id": shared_conv1_msg.sender_id,
                    "created_at": shared_conv1_msg.created_at.isoformat(),
                },
                "unread_count": 0
            },
            {
                "conversation_id": shared_conv2.id,
                "last_message": {
                    "id": shared_conv2_msg2.id,
                    "text": shared_conv2_msg2.text,
                    "sender_id": shared_conv2_msg2.sender_id,
                    "created_at": shared_conv2_msg2.created_at.isoformat(),
                },
                "unread_count": 1
            },
            {
                "conversation_id": shared_conv3.id,
                "last_message": {
                    "id": shared_conv3_msg.id,
                    "text": shared_conv3_msg.text,
                    "sender_id": shared_conv3_msg.sender_id,
                    "created_at": shared_conv3_msg.created_at.isoformat(),
                },
                "unread_count": 1
            }
        )
    )
