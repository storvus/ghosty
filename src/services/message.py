import logging

from src.aliases import UserId
from src.events import OutgoingMessageEvent
from src.repositories.message import MessageRepository
from src.repositories.user import UserRepository
from src.state import AppState

logger = logging.getLogger(__name__)


class MessageService:
    def __init__(
        self, db_session, message_repo: MessageRepository, user_repo: UserRepository
    ):
        self.db_session = db_session
        self.message_repo = message_repo
        self.user_repo = user_repo

    async def incoming_message(
        self, message_client_id: str, from_uid: UserId, to_uid: UserId, text: str
    ) -> OutgoingMessageEvent:
        logger.info("Sending message to user %s: %s", to_uid, text)
        message = await self.message_repo.create_message(from_uid, to_uid, text)
        await self.db_session.commit()

        from_user = await self.user_repo.get_user_by_id(from_uid)
        # ToDo: handle offline users, store messages, etc.
        # ToDo: validate if from_user can even send message to to_user, e.g. if they are friends, etc.
        # ToDo: validate if to_user exists, etc.
        return OutgoingMessageEvent(
            client_id=client_id,
            server_id=message.id,
            from_uid=from_uid,
            from_username=from_user.username,
            to_uid=to_uid,
            message=text,
        )
