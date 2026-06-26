import logging
from collections import defaultdict

from src.aliases import UserId
from src.constants import Presence
from src.dataclass import ClientSession

logger = logging.getLogger(__name__)


class AppState:
    def __init__(self):
        self.connections: dict[UserId, list[ClientSession]] = defaultdict(list)
        self.presence_by_user: dict[UserId, Presence] = {}

    def set_presence(self, user_id: UserId, presence: Presence):
        logger.info("Setting presence for user %s to %s", user_id, presence)
        self.presence_by_user[user_id] = presence

    def get_presence(self, user_id: UserId) -> Presence | None:
        return self.presence_by_user.get(user_id)

    def add_connection(self, peer_session: ClientSession):
        if peer_session not in self.connections[peer_session.user_id]:
            self.connections[peer_session.user_id].append(peer_session)

    def get_user_connections(self, user_id: UserId) -> list[ClientSession]:
        return self.connections.get(user_id, [])

    def remove_connection(self, peer_session: ClientSession):
        if peer_session.user_id in self.connections:
            self.connections[peer_session.user_id].remove(peer_session)
            if not self.connections[peer_session.user_id]:
                del self.connections[peer_session.user_id]
                del self.presence_by_user[peer_session.user_id]

    async def get_friend_user_ids(self, user_id: UserId) -> list[UserId]:
        return list(self.connections.keys())

    async def get_invisible_exception_user_ids(self, user_id: UserId) -> list[UserId]:
        return []


main_app_state = AppState()
