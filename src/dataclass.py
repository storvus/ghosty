import uuid
from dataclasses import dataclass, field

from starlette.websockets import WebSocket

from src.aliases import UserId
from src.constants import ConnectionState


@dataclass
class ClientSession:
    ws: WebSocket
    user_id: UserId
    state: ConnectionState
    device_id: str | None = None
    connection_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def set_state(self, new_state: ConnectionState):
        self.state = new_state
