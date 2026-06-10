from src.dataclass import ClientSession
from src.events import IncomingMessageEvent, OutgoingMessageEvent
from src.services.message import MessageService


async def handle_message(
    message_service: MessageService, event: IncomingMessageEvent, peer_session: ClientSession
) -> list[OutgoingMessageEvent]:
    return await message_service.incoming_message(peer_session.user_id, event)
