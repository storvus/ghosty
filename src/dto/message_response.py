from pydantic import BaseModel


class MessageResponse(BaseModel):
    id: int
    # client_message_id: str
    text: str
    sender_id: int
    created_at: str
