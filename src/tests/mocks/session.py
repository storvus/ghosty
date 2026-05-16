from dataclasses import dataclass

from starlette.websockets import WebSocket

from src.constants import ConnectionState


@dataclass
class MockedClientSession:
    user_id: str
    state: ConnectionState
    ws: WebSocket | None = None
