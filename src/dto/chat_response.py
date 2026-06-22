from pydantic import BaseModel

from src.dto.message_response import MessageResponse
from src.models import User


class ChatResponse(BaseModel):
    conversation_id: int
    # title: str
    last_message: MessageResponse | None
    # avatar_url: str | None = None
    unread_count: int
