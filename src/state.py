import logging
from collections import defaultdict

from src.aliases import UserId
from src.constants import Presence
from src.dataclass import ClientSession

logger = logging.getLogger(__name__)


class AppState:
    def __init__(self):
        self.connections: dict[UserId, set[ClientSession]] = defaultdict(set)
        self.presence_by_user: dict[UserId, Presence] = {}

    def set_presence(self, user_id: UserId, presence: Presence):
        logger.info("Setting presence for user %s to %s", user_id, presence)
        self.presence_by_user[user_id] = presence

    def get_presence(self, user_id: UserId) -> Presence:
        return self.presence_by_user.get(user_id)

    def add_connection(self, peer_session: ClientSession):
        self.connections[peer_session.user_id].add(peer_session)
        print(self.connections)

    def get_user_connections(self, user_id: UserId):
        return self.connections.get(user_id, set())

    def get_connections(self):
        return self.connections

    def remove_connection(self, peer_session: ClientSession):
        if peer_session.user_id in self.connections:
            self.connections[peer_session.user_id].discard(peer_session)
            if not self.connections[peer_session.user_id]:
                del self.connections[peer_session.user_id]
                del self.presence_by_user[peer_session.user_id]

    async def get_friend_user_ids(self, user_id: UserId) -> list[UserId]:
        return list(self.connections.keys())

    async def get_invisible_exception_user_ids(self, user_id: UserId) -> list[UserId]:
        return []
