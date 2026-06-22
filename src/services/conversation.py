import logging

from IPython.core.magics import history
from fastapi import HTTPException

from src.dto.chat_response import ChatResponse
from src.dto.current_user import CurrentUser
from src.dto.message_response import MessageResponse
from src.repositories.conversation import ConversationRepository
from src.repositories.message import MessageRepository

logger = logging.getLogger(__name__)


class ConversationService:
    def __init__(self, db_session, conversation_repo: ConversationRepository, message_repo: MessageRepository):
        self.db_session = db_session
        self.conversation_repo = conversation_repo
        self.message_repo = message_repo

    async def get_user_conversations(self, user: CurrentUser) -> list[ChatResponse]:
        logger.info(f"Fetching conversations for user {user.id}")
        return await self.conversation_repo.get_conversations_for_user_id(user.id)

    async def get_history(self, user: CurrentUser, conversation_id: int, before_message_id: int) -> list[MessageResponse]:
        # check if the user is allowed to read from this conversation
        if not await self.conversation_repo.is_participant(user.id, conversation_id):
            logger.warning(f"User {user.id} is not a participant of conversation {conversation_id}")
            raise HTTPException(status_code=403, detail="Forbidden")

        messages = await self.message_repo.get_history(conversation_id, before_message_id)
        return [
            MessageResponse(
                id=message.id,
                text=message.text,
                sender_id=message.sender_id,
                created_at=message.created_at.isoformat(),
            )
            for message in messages
        ]

