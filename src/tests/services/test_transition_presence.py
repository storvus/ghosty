import pytest

from src.constants import Presence
from src.events import PresenceBroadcastEvent, PresenceSyncEvent
from src.services.presence import PresenceService


@pytest.mark.asyncio
async def test__disconnect__active_sessions_exist(app_state):
    """
    If a user disconnects but still has active sessions, their presence should be set to OFFLINE
    but no broadcast should be sent to their friends.
    """
    presence_service = PresenceService(app_state)
    events = await presence_service.transition_presence("user1", Presence.OFFLINE)
    assert events == []


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "current_presence",
    [
        Presence.INVISIBLE,
        Presence.INVISIBLE_EXCEPT,
    ],
)
async def test__disconnect__no_sessions_exist__invisible(app_state, current_presence):
    """
    If a user disconnects and has no active sessions but is currently invisible, their presence should not change
    and no broadcast should be sent to their friends.
    """
    app_state.get_presence.return_value = current_presence
    app_state.get_user_connections.return_value = []
    presence_service = PresenceService(app_state)
    events = await presence_service.transition_presence("user1", Presence.OFFLINE)
    assert events == []


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "current_presence",
    [
        Presence.ONLINE,
        Presence.DO_NOT_DISTURB,
        Presence.AWAY,
    ],
)
async def test__disconnect__no_sessions_exist__non_invisible(
    app_state, current_presence
):
    """
    If a user disconnects and has no active sessions and is currently not invisible,
    their presence should be set to OFFLINE
    """
    app_state.get_presence.return_value = current_presence
    app_state.get_user_connections.return_value = []
    presence_service = PresenceService(app_state)
    events = await presence_service.transition_presence("user1", Presence.OFFLINE)
    assert events == [
        PresenceBroadcastEvent(
            subject_user_id="user1",
            audience_user_ids=["friend1", "friend2"],
            presence=Presence.OFFLINE,
        )
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "new_presence",
    [
        Presence.ONLINE,
        Presence.DO_NOT_DISTURB,
        Presence.AWAY,
    ],
)
async def test__change_status_to_online__sync_session_and_broadcast(
    app_state, new_presence
):
    """
    If a user changes their presence to an online status, it should update their presence
    and broadcast the new presence to their friends.
    """
    presence_service = PresenceService(app_state)
    events = await presence_service.transition_presence("user1", new_presence)
    assert events == [
        PresenceSyncEvent(user_id="user1", presence=new_presence),
        PresenceBroadcastEvent(
            subject_user_id="user1",
            audience_user_ids=["friend1", "friend2"],
            presence=new_presence,
        ),
    ]


@pytest.mark.asyncio
async def test__change_status_to_invisible__sync_session_and_broadcast_offline(
    app_state,
):
    """
    If a user changes their presence to invisible, it should update their presence to invisible and
    broadcast the new presence as offline to their friends.
    """
    presence_service = PresenceService(app_state)
    events = await presence_service.transition_presence("user1", Presence.INVISIBLE)
    assert events == [
        PresenceSyncEvent(user_id="user1", presence=Presence.INVISIBLE),
        PresenceBroadcastEvent(
            subject_user_id="user1",
            audience_user_ids=["friend1", "friend2"],
            presence=Presence.OFFLINE,
        ),
    ]


@pytest.mark.asyncio
async def test__change_status_to_invisible_except__sync_session_and_broadcast(
    app_state,
):
    """
    If a user changes their presence to invisible except, it should update their presence to invisible except and
    broadcast the new presence as offline to their friends or online to exception list.
    """
    presence_service = PresenceService(app_state)
    events = await presence_service.transition_presence(
        "user1", Presence.INVISIBLE_EXCEPT
    )
    assert events == [
        PresenceSyncEvent(user_id="user1", presence=Presence.INVISIBLE_EXCEPT),
        PresenceBroadcastEvent(
            subject_user_id="user1",
            audience_user_ids=["friend1"],
            presence=Presence.OFFLINE,
        ),
        PresenceBroadcastEvent(
            subject_user_id="user1",
            audience_user_ids=["friend2"],
            presence=Presence.ONLINE,
        ),
    ]
