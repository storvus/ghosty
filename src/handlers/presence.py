from src.constants import Presence
from src.dataclass import ClientSession
from src.events import PresenceBroadcastEvent, PresenceEvent, PresenceSyncEvent
from src.services.presence import PresenceService
from src.state import AppState


async def handle_presence(
    presence_service: PresenceService,
    event: PresenceEvent,
    peer_session: ClientSession,
    app_state: AppState,
) -> list[PresenceBroadcastEvent | PresenceSyncEvent]:
    return await presence_service.transition_presence(
        peer_session.user_id, event.presence
    )


async def handle_disconnect(
    presence_service: PresenceService, peer_session, app_state
) -> list[PresenceBroadcastEvent | PresenceSyncEvent]:
    app_state.remove_connection(peer_session)
    return await presence_service.transition_presence(
        peer_session.user_id, Presence.OFFLINE
    )
