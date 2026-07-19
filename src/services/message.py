import logging

from asyncpg import UniqueViolationError
from sqlalchemy.ext.asyncio import AsyncSession

from src.dto.current_user import CurrentUser
from src.dto.outgoing_envelope import OutgoingEnvelope
from src.events import IncomingMessageEvent
from src.models.conversation import ConversationType
from src.payloads._user_info import UserInfo
from src.payloads.message_ack import MessageAckPayload
from src.payloads.new_message import NewMessagePayload
from src.repositories.conversation import ConversationRepository
from src.repositories.message import MessageRepository
from src.repositories.user import UserRepository

logger = logging.getLogger(__name__)


class MessageService:
    def __init__(
        self, db_session: AsyncSession, message_repo: MessageRepository, user_repo: UserRepository, conversation_repo: ConversationRepository
    ):
        self.db_session = db_session
        self.message_repo = message_repo
        self.user_repo = user_repo
        self.conversation_repo = conversation_repo

    async def incoming_message(self, current_user: CurrentUser, event: IncomingMessageEvent) -> list[OutgoingEnvelope]:
        if event.conversation_id:
            if not await self.conversation_repo.is_participant(current_user.id, event.conversation_id):
                logger.warning(
                    f"User {current_user.id} is not a participant of conversation {event.conversation_id} "
                    f"or the conversation does not exist. Ignoring the message."
                )
                return []
            # ToDo: add a check that current_user isn't banned for the conversation

            conversation_id = event.conversation_id
        elif event.recipient_id:
            if not await self.user_repo.get_by_id(event.recipient_id):
                logger.warning(f"Recipient user {event.recipient_id} does not exist. Ignoring the message.")
                return []
            conversation = await self.conversation_repo.get_direct_conversation_between_users(current_user.id, event.recipient_id)
            if not conversation:
                conversation = await self.conversation_repo.create_conversation([current_user.id, event.recipient_id], type=ConversationType.direct)
                await self.db_session.commit()
            # ToDo: add a check that current_user isn't banned for the conversation
            # ToDo: add a check that current_user isn't banned for the user

            conversation_id = conversation.id
        else:
            logger.warning(
                f"Incoming message from user {current_user.id} does not have a conversation_id or recipient_id. Ignoring the message."
            )
            return []

        try:
            message = await self.message_repo.create_message(
                client_message_id=event.client_message_id,
                sender_id=current_user.id,
                conversation_id=conversation_id,
                text=event.message,
            )
            await self.db_session.commit()
        except UniqueViolationError:
            await self.db_session.rollback()
            message = await self.message_repo.get_by_client_message_id(event.client_message_id, current_user.id)

        participants = await self.conversation_repo.get_conversation_participants(conversation_id)

        message_ack = OutgoingEnvelope(
            payload=MessageAckPayload(
                conversation_id=conversation_id,
                client_message_id=event.client_message_id,
                message_id=message.id,
                created_at=message.created_at.isoformat(),
            ),
            user_ids=[current_user.id]
        )

        new_message = OutgoingEnvelope(
            payload=NewMessagePayload(
                conversation_id=conversation_id,
                message_id=message.id,
                text=message.text,
                created_at=message.created_at.isoformat(),
                sender=UserInfo.from_dict(current_user.to_dict())
            ),
            user_ids=[p.user_id for p in participants]
        )
        return [message_ack, new_message]
