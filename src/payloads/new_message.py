from pydantic import BaseModel

from src.payloads._user_info import UserInfo


class NewMessagePayload(BaseModel):
    type: str = "new_message"
    conversation_id: int
    message_id: int
    text: str
    sender: UserInfo
    created_at: str
