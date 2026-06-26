import asyncio

from src.dataclass import ClientSession
from src.dto.outgoing_envelope import OutgoingEnvelope
from src.serializers.events import event_serializer
from src.state import AppState


class ConnectionManager:
    def __init__(self, app_state: AppState):
        self.app_state = app_state

    async def send(self, envelope: OutgoingEnvelope):
        user_sessions: list[ClientSession] = []
        if envelope.user_ids:
            user_sessions.extend([
                user_session
                for user_id in envelope.user_ids
                for user_session in self.app_state.get_user_connections(user_id)
            ])
        if envelope.connection_ids:
            user_sessions.extend([
                user_session
                for user_id in envelope.connection_ids
                for user_session in self.app_state.get_user_connections(user_id)
            ])

        payload = event_serializer.serialize(envelope.payload)
        print(f"Sending event to {len(user_sessions)} sessions: {payload}")
        await self._send_many(user_sessions, payload)

    async def _send_many(self, user_sessions: list[ClientSession], payload: dict):
        await asyncio.gather(
            *(user_session.ws.send_json(payload) for user_session in user_sessions),
            return_exceptions=True,
        )
