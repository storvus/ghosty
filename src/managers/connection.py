import asyncio

from src.dataclass import ClientSession
from src.events import PresenceBroadcastEvent, PresenceSyncEvent, SendMessageEvent
from src.serializers.events import event_serializer
from src.state import AppState


class ConnectionManager:
    def __init__(self, app_state: AppState):
        self.app_state = app_state

    async def send(self, event: SendMessageEvent | PresenceSyncEvent | PresenceBroadcastEvent):
        match event:
            case SendMessageEvent():
                user_sessions = self.app_state.get_user_connections(event.to_user_id)

            case PresenceSyncEvent():
                user_sessions = self.app_state.get_user_connections(event.user_id)

            case PresenceBroadcastEvent():
                # ToDo: to send to those who is online?
                user_sessions = [
                    user_session
                    for user_id in event.audience_user_ids
                    for user_session in self.app_state.get_user_connections(user_id)
                ]

            case _:
                raise ValueError(f"Unsupported event type: {type(event)}")

        payload = event_serializer.serialize(event)
        await self._send_many(user_sessions, payload)

    async def _send_many(self, user_sessions: list[ClientSession], payload: dict):
        await asyncio.gather(
            *(user_session.ws.send_json(payload) for user_session in user_sessions), return_exceptions=True
        )
