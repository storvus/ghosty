import logging

from IPython.core.magics import history
from fastapi import HTTPException

from src.dto.chat_response import ConversationRow, ConversationResponse
from src.dto.current_user import CurrentUser
from src.dto.message_response import MessageResponse
from src.dto.user_response import UserResponse
from src.models.conversation import ConversationType
from src.repositories.conversation import ConversationRepository
from src.repositories.message import MessageRepository
from src.repositories.user import UserRepository

logger = logging.getLogger(__name__)


class ConversationService:
    def __init__(self, db_session, conversation_repo: ConversationRepository, message_repo: MessageRepository, user_repo: UserRepository):
        self.db_session = db_session
        self.conversation_repo = conversation_repo
        self.message_repo = message_repo
        self.user_repo = user_repo

    async def get_user_conversations(self, current_user: CurrentUser) -> list[ConversationResponse]:
        logger.info(f"Fetching conversations for user {current_user.id}")
        conversations = await self.conversation_repo.get_conversations_for_user_id(current_user.id)
        user_ids = [user_id for conversation in conversations for user_id in conversation.participant_ids]
        users = await self.user_repo.get_by_ids(user_ids)
        user_map = {user.id: user for user in users}

        response = []
        for conversation in conversations:
            if conversation.type == ConversationType.direct:
                other_user_id = next(user_id for user_id in conversation.participant_ids if user_id != current_user.id)
                title = user_map[other_user_id].username
            else:
                title = f"Members {len(conversation.participant_ids)}"

            response.append(
                ConversationResponse(
                    **conversation.__dict__,
                    participants=[UserResponse.from_user(user_map[user_id]) for user_id in conversation.participant_ids],
                    title=title
                )
            )
        return response

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

