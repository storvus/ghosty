from datetime import datetime, timedelta, timezone

import jwt
from hamcrest import assert_that, is_, has_length
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.models import User
from src.utils import create_token

URL_TEMPLATE = "/api/chats/{chat_id}/history?before_message_id={before_message_id}"

# ---------------------------------------------------------------------------
# Auth errors
# ---------------------------------------------------------------------------
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_history_no_auth_header(async_client: AsyncClient):
    response = await async_client.get(URL_TEMPLATE.format(chat_id="1", before_message_id="1"))
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_history_invalid_token(async_client: AsyncClient):
    response = await async_client.get(URL_TEMPLATE.format(chat_id="1", before_message_id="1"), headers={"Authorization": "Bearer not.a.valid.token"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"


@pytest.mark.asyncio
async def test_get_history_expired_token(async_client: AsyncClient, user: User):
    payload = {"user_id": user.id, "exp": datetime.now(timezone.utc) - timedelta(seconds=1)}
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.TOKEN_ENCODE_ALGORITHM)
    response = await async_client.get(URL_TEMPLATE.format(chat_id="1", before_message_id="1"), headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Token expired"


@pytest.mark.asyncio
async def test_get_history_token_for_nonexistent_user(async_client: AsyncClient):
    token = create_token(999_999_999)
    response = await async_client.get(URL_TEMPLATE.format(chat_id="1", before_message_id="1"), headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert response.json()["detail"] == "User not found"


@pytest.mark.asyncio
async def test_get_history_nonexistent_chat(async_client: AsyncClient, auth_headers: dict):
    response = await async_client.get(URL_TEMPLATE.format(chat_id="1", before_message_id="1"), headers=auth_headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "Forbidden"


@pytest.mark.asyncio
async def test_get_history_not_participant_of_chat(
    async_client: AsyncClient,
    auth_headers: dict,
    make_conversation,
    build_user,
):
    user = await build_user()
    other_user = await build_user()
    conversation = await make_conversation(user, other_user)
    # auth_headers is for the third user
    response = await async_client.get(URL_TEMPLATE.format(chat_id=conversation.id, before_message_id="1"), headers=auth_headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "Forbidden"


@pytest.mark.asyncio
async def test_get_history_empty_chat(
    async_client: AsyncClient,
    auth_headers: dict,
    user: User,
    make_conversation,
    build_user,
):
    other_user = await build_user()
    conversation = await make_conversation(user, other_user)
    # auth_headers is for the third user
    response = await async_client.get(URL_TEMPLATE.format(chat_id=conversation.id, before_message_id="1"), headers=auth_headers)
    assert_that(response.status_code, is_(200))
    assert_that(response.json(), is_([]))


@pytest.mark.asyncio
async def test_get_history_limit_is_respected(
    db_session: AsyncSession,
    async_client: AsyncClient,
    auth_headers: dict,
    user: User,
    make_conversation,
    make_message,
    build_user,
):
    user2 = await build_user()

    user_user2_conversation = await make_conversation(user, user2)
    all_messages = []
    for _ in range(30):
        all_messages.append(await make_message(user, user_user2_conversation))
        all_messages.append(await make_message(user2, user_user2_conversation))
    await db_session.commit()
    all_messages.sort(key=lambda m: m.id, reverse=True)

    response = await async_client.get(URL_TEMPLATE.format(chat_id=user_user2_conversation.id, before_message_id=all_messages[0].id + 1), headers=auth_headers)
    assert_that(response.status_code, is_(200))
    messages = response.json()
    assert_that(messages, has_length(50))
    assert_that(response.json(), is_([
        {
            "id": msg.id,
            "text": msg.text,
            "sender_id": msg.sender_id,
            "created_at": msg.created_at.isoformat()
        } for msg in all_messages[:50]
    ]))

    response = await async_client.get(URL_TEMPLATE.format(chat_id=user_user2_conversation.id, before_message_id=all_messages[50].id + 1), headers=auth_headers)
    assert_that(response.status_code, is_(200))
    messages = response.json()
    assert_that(messages, has_length(10))
    assert_that(response.json(), is_([
        {
            "id": msg.id,
            "text": msg.text,
            "sender_id": msg.sender_id,
            "created_at": msg.created_at.isoformat()
        } for msg in all_messages[50:]
    ]))


@pytest.mark.asyncio
async def test_get_history_visible_for_both_participants(
    db_session: AsyncSession,
    async_client: AsyncClient,
    user: User,
    make_conversation,
    make_message,
    build_user,
):
    user2 = await build_user()
    user3 = await build_user()

    user_user2_conversation = await make_conversation(user, user2)
    user_user2_conversation_msg = await make_message(user, user_user2_conversation)
    user_user2_conversation_msg2 = await make_message(user2, user_user2_conversation)
    await make_message(user2, user_user2_conversation)

    user_user2_conversation2 = await make_conversation(user, user2)
    await make_message(user, user_user2_conversation2)
    await make_message(user2, user_user2_conversation2)

    user2_user3_conversation2 = await make_conversation(user2, user3)
    await make_message(user2, user2_user3_conversation2)
    await make_message(user3, user2_user3_conversation2)
    await db_session.commit()

    both_participants = (user, user2)
    for participant in both_participants:
        auth_headers = {"Authorization": f"Bearer {create_token(participant.id)}"}
        # don't include the `before_message_id` itself
        response = await async_client.get(URL_TEMPLATE.format(chat_id=user_user2_conversation.id, before_message_id=user_user2_conversation_msg.id), headers=auth_headers)
        assert_that(response.status_code, is_(200))
        assert_that(response.json(), is_([]))

        response = await async_client.get(URL_TEMPLATE.format(chat_id=user_user2_conversation.id, before_message_id=user_user2_conversation_msg2.id + 1), headers=auth_headers)
        assert_that(response.status_code, is_(200))
        # the order matters & no other conversations are returned
        assert_that(response.json(), is_([
            {
                "id": user_user2_conversation_msg2.id,
                "text": user_user2_conversation_msg2.text,
                "sender_id": user_user2_conversation_msg2.sender_id,
                "created_at": user_user2_conversation_msg2.created_at.isoformat()
            },
            {
                "id": user_user2_conversation_msg.id,
                "text": user_user2_conversation_msg.text,
                "sender_id": user_user2_conversation_msg.sender_id,
                "created_at": user_user2_conversation_msg.created_at.isoformat()
            }
        ]))
