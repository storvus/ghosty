import logging

from src.aliases import UserId
from src.constants import Presence
from src.events import PresenceBroadcastEvent, PresenceSyncEvent
from src.state import AppState

logger = logging.getLogger(__name__)

INVISIBLE_PRESENCES = {Presence.INVISIBLE, Presence.INVISIBLE_EXCEPT}
ONLINE_PRESENCES = {Presence.ONLINE, Presence.AWAY, Presence.DO_NOT_DISTURB}


class PresenceService:
    def __init__(self, app_state: AppState):
        self.app_state = app_state
        # ToDo: to handle presence subscriptions, e.g. to broadcast presence only to friends, etc.
        self.audience = None

    # ToDo: cover with logs and comments
    async def transition_presence(
        self, user_id: UserId, new_presence: Presence
    ) -> list[PresenceBroadcastEvent | PresenceSyncEvent]:
        events: list[PresenceBroadcastEvent | PresenceSyncEvent] = []

        current_presence = self.app_state.get_presence(user_id)
        active_sessions = self.app_state.get_user_connections(user_id)
        friend_user_ids = await self.app_state.get_friend_user_ids(user_id)

        if new_presence == Presence.OFFLINE:
            logger.info(
                "User %s is going offline, checking active sessions and current presence",
                user_id,
            )
            if active_sessions:
                logger.info(
                    "User %s still has active sessions, skipping presence update and broadcast",
                    user_id,
                )
                return []

            if current_presence in INVISIBLE_PRESENCES:
                logger.info(
                    "User %s was invisible, skipping presence update and broadcast",
                    user_id,
                )
                return []
            msg = (
                "User %s has no active sessions and is not invisible, "
                "setting presence to OFFLINE and broadcasting to friends"
            )
            logger.info(msg, user_id)
            events.append(
                PresenceBroadcastEvent(
                    subject_user_id=user_id,
                    audience_user_ids=friend_user_ids,
                    presence=new_presence,
                )
            )
            return events

        self.app_state.set_presence(user_id, new_presence)

        events.append(PresenceSyncEvent(user_id=user_id, presence=new_presence))

        if new_presence in ONLINE_PRESENCES:
            events.append(
                PresenceBroadcastEvent(
                    subject_user_id=user_id,
                    audience_user_ids=friend_user_ids,
                    presence=new_presence,
                )
            )
            return events

        if new_presence == Presence.INVISIBLE:
            events.append(
                PresenceBroadcastEvent(
                    subject_user_id=user_id,
                    audience_user_ids=friend_user_ids,
                    presence=Presence.OFFLINE,
                )
            )
            return events

        if new_presence == Presence.INVISIBLE_EXCEPT:
            exception_user_ids = await self.app_state.get_invisible_exception_user_ids(
                user_id
            )

            normal_user_ids = [
                friend_id
                for friend_id in friend_user_ids
                if friend_id not in exception_user_ids
            ]

            events.append(
                PresenceBroadcastEvent(
                    subject_user_id=user_id,
                    audience_user_ids=normal_user_ids,
                    presence=Presence.OFFLINE,
                )
            )

            events.append(
                PresenceBroadcastEvent(
                    subject_user_id=user_id,
                    audience_user_ids=exception_user_ids,
                    presence=Presence.ONLINE,
                )
            )

            return events

        raise ValueError(f"Unsupported presence: {new_presence}")
