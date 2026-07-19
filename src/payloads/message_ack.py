from pydantic import BaseModel

class MessageAckPayload(BaseModel):
    type: str = "message_ack"
    conversation_id: int
    client_message_id: str
    message_id: int
    created_at: str
