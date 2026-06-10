# import logging
#
# from src.dataclass import ClientSession
# from src.events import (
#     HeartbeatEvent,
#     HelloEvent,
#     IncomingMessageEvent,
#     PresenceBroadcastEvent,
#     PresenceEvent,
#     PresenceSyncEvent,
#     OutgoingMessageEvent,
# )
# from src.handlers.hello import handle_hello
# from src.handlers.message import handle_message
# from src.handlers.presence import handle_presence
# from src.services.message import MessageService
# from src.services.presence import PresenceService
# from src.state import AppState
#
# logger = logging.getLogger(__name__)
#
#
# async def dispatch_event(
#     message_service: MessageService,
#     presence_service: PresenceService,
#     event: IncomingMessageEvent | PresenceEvent | HeartbeatEvent | HelloEvent,
#     peer_session: ClientSession,
#     app_state: AppState,
# ) -> list[OutgoingMessageEvent | PresenceSyncEvent | PresenceBroadcastEvent]:
#     match event:
#         case IncomingMessageEvent():
#             return await handle_message(message_service, event, peer_session)
#         case PresenceEvent():
#             raise NotImplementedError("not implemented yet")
#             return await handle_presence(
#                 presence_service, event, peer_session, app_state
#             )
#         case HelloEvent():
#             raise NotImplementedError("not implemented yet")
#             return await handle_hello(event, peer_session, app_state)
#         case HeartbeatEvent():
#             raise NotImplementedError("Heartbeat handling not implemented yet")
#         case _:
#             logger.warning("Received unsupported event type: %s", type(event))
#             raise ValueError(f"Unsupported event type: {type(event)}")
