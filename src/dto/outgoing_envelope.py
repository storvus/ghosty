from dataclasses import dataclass

from src.payloads.connected import SessionConnectedPayload
from src.payloads.message_ack import MessageAckPayload
from src.payloads.new_message import NewMessagePayload

OutgoingPayload = MessageAckPayload | NewMessagePayload | SessionConnectedPayload


@dataclass
class OutgoingEnvelope:
    payload: OutgoingPayload
    user_ids: list[int]

    @property
    def type(self) -> str:
        return self.payload.type
