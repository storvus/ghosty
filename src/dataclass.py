from dataclasses import dataclass

from starlette.websockets import WebSocket

from src.aliases import UserId
from src.constants import ConnectionState


@dataclass
class ClientSession:
    ws: WebSocket
    user_id: UserId
    state: ConnectionState
    device_id: str | None = None

    def set_state(self, new_state: ConnectionState):
        self.state = new_state

    def __hash__(self):
        return id(self.ws)
