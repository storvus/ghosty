from src.constants import ConnectionState
from src.events import PresenceBroadcastEvent, PresenceSyncEvent
from src.services.presence import PresenceService


async def handle_hello(
    event, peer_session, app_state
) -> list[PresenceBroadcastEvent | PresenceSyncEvent]:
    peer_session.set_state(ConnectionState.HELLO_RECEIVED)

    presence_service = PresenceService(app_state)
    app_state.add_connection(peer_session)
    peer_session.set_state(ConnectionState.ACTIVE)
    # ToDo: we may want to sync presence from already active sessions instead
    return await presence_service.transition_presence(
        peer_session.user_id, event.presence
    )
