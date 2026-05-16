import logging

from src.constants import ConnectionState, Presence
from src.dataclass import ClientSession
from src.events import (
    HeartbeatEvent,
    HelloEvent,
    MessageEvent,
    PresenceBroadcastEvent,
    PresenceEvent,
    PresenceSyncEvent,
    SendMessageEvent,
)
from src.services.message import MessageService
from src.services.presence import PresenceService
from src.state import AppState

logger = logging.getLogger(__name__)


async def handle_message(
    event: MessageEvent, peer_session: ClientSession, app_state: AppState
) -> list[SendMessageEvent]:
    return [MessageService(app_state).incoming_message(peer_session.user_id, event.recipient_id, event.message)]


async def handle_presence(
    event: PresenceEvent, peer_session: ClientSession, app_state: AppState
) -> list[PresenceBroadcastEvent | PresenceSyncEvent]:
    presence_service = PresenceService(app_state)
    return await presence_service.transition_presence(peer_session.user_id, event.presence)


async def handle_disconnect(peer_session, app_state) -> list[PresenceBroadcastEvent | PresenceSyncEvent]:
    app_state.remove_connection(peer_session)
    presence_service = PresenceService(app_state)
    return await presence_service.transition_presence(peer_session.user_id, Presence.OFFLINE)


async def handle_hello(event, peer_session, app_state) -> list[PresenceBroadcastEvent | PresenceSyncEvent]:
    peer_session.set_state(ConnectionState.HELLO_RECEIVED)

    presence_service = PresenceService(app_state)
    app_state.add_connection(peer_session)
    peer_session.set_state(ConnectionState.ACTIVE)
    # ToDo: we may want to sync presence from already active sessions instead
    return await presence_service.transition_presence(peer_session.user_id, event.presence)


async def dispatch_event(
    event: MessageEvent | PresenceEvent | HeartbeatEvent | HelloEvent, peer_session: ClientSession, app_state: AppState
) -> list[SendMessageEvent | PresenceSyncEvent | PresenceBroadcastEvent]:
    match event:
        case MessageEvent():
            return await handle_message(event, peer_session, app_state)
        case PresenceEvent():
            return await handle_presence(event, peer_session, app_state)
        case HelloEvent():
            return await handle_hello(event, peer_session, app_state)
        case HeartbeatEvent():
            raise NotImplementedError("Heartbeat handling not implemented yet")
        case _:
            logger.warning("Received unsupported event type: %s", type(event))
            raise ValueError(f"Unsupported event type: {type(event)}")
