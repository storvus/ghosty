import logging

from src.dto.current_user import CurrentUser
from src.dto.outgoing_envelope import OutgoingEnvelope
from src.events import IncomingMessageEvent
from src.services.message import MessageService

logger = logging.getLogger(__name__)


async def dispatch_event(
    current_user: CurrentUser,
    message_service: MessageService,
    event: IncomingMessageEvent, # | PresenceEvent | HeartbeatEvent | HelloEvent,
) -> list[OutgoingEnvelope]:
    match event:
        case IncomingMessageEvent():
            return await message_service.incoming_message(current_user, event)
        # case PresenceEvent():
        #     raise NotImplementedError("not implemented yet")
        #     return await handle_presence(
        #         presence_service, event, peer_session, app_state
        #     )
        # case HelloEvent():
        #     raise NotImplementedError("not implemented yet")
        #     return await handle_hello(event, peer_session, app_state)
        # case HeartbeatEvent():
        #     raise NotImplementedError("Heartbeat handling not implemented yet")
        case _:
            logger.warning("Received unsupported event type: %s", type(event))
            raise ValueError(f"Unsupported event type: {type(event)}")
