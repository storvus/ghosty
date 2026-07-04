from pydantic import BaseModel

from src.dto.message_response import MessageResponse
from src.dto.user_response import UserResponse
from src.models.conversation import ConversationType


class ConversationRow(BaseModel):
    conversation_id: int
    last_read_message_id: int | None
    participant_ids: list[int]
    type: ConversationType
    last_message: MessageResponse | None
    unread_count: int


class ConversationResponse(BaseModel):
    conversation_id: int
    last_read_message_id: int | None
    participants: list[UserResponse]
    type: ConversationType
    title: str
    last_message: MessageResponse | None
    unread_count: int
