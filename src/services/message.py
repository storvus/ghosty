import logging

from src.aliases import UserId
from src.events import SendMessageEvent
from src.state import AppState

logger = logging.getLogger(__name__)


class MessageService:
    def __init__(self, app_state: AppState):
        self.app_state = app_state
        # ToDo: to handle presence subscriptions, e.g. to broadcast presence only to friends, etc.
        self.audience = None

    def incoming_message(self, from_user_id: UserId, to_user_id: UserId, message: str) -> SendMessageEvent:
        logger.info("Sending message to user %s: %s", to_user_id, message)

        # ToDo: handle offline users, store messages, etc.
        # ToDo: validate if from_user can even send message to to_user, e.g. if they are friends, etc.
        # ToDo: validate if to_user exists, etc.
        return SendMessageEvent(from_user_id=from_user_id, to_user_id=to_user_id, message=message)
