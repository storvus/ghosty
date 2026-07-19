import asyncio

from src.dataclass import ClientSession
from src.dto.outgoing_envelope import OutgoingEnvelope, OutgoingPayload
from src.state import AppState


class ConnectionManager:
    def __init__(self, app_state: AppState):
        self.app_state = app_state

    async def send_to_session(self, envelope: OutgoingEnvelope, session: ClientSession):
        return await self._send_many([session], envelope.payload)

    async def send(self, envelope: OutgoingEnvelope, exclude_connection_ids: list[str] | None = None):
        if exclude_connection_ids is None:
            exclude_connection_ids = []

        user_sessions = [
            user_session
            for user_id in envelope.user_ids
            for user_session in self.app_state.get_user_connections(user_id)
            if user_session.connection_id not in exclude_connection_ids
        ]
        await self._send_many(user_sessions, envelope.payload)

    @staticmethod
    async def _send_many(user_sessions: list[ClientSession], payload: OutgoingPayload):
        data = payload.model_dump()
        await asyncio.gather(
            *(user_session.ws.send_json(data) for user_session in user_sessions),
            return_exceptions=True,
        )
