from src.constants import MessageType
from src.events import PresenceBroadcastEvent, PresenceSyncEvent, OutgoingMessageEvent


class EventSerializer:
    def __init__(self):
        self._handlers = {}

    def register(self, event_type):
        def wrapper(fn):
            self._handlers[event_type] = fn
            return fn

        return wrapper

    def serialize(self, event):
        fn = self._handlers[type(event)]
        return fn(event)


event_serializer = EventSerializer()


@event_serializer.register(OutgoingMessageEvent)
def send_message_serializer(e):
    return {
        "type": MessageType.MESSAGE,
        "from_uid": e.from_uid,
        "from_username": e.from_username,
        "message": e.message,
    }


@event_serializer.register(PresenceSyncEvent)
def sync_presence_serializer(e):
    return {
        "type": MessageType.SYNC_PRESENCE,
        "presence": e.presence,
    }


@event_serializer.register(PresenceBroadcastEvent)
def notify_presence_serializer(e):
    return {
        "type": MessageType.NOTIFY_PRESENCE,
        "subject_user_id": e.subject_user_id,
        "presence": e.presence,
    }
