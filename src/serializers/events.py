from src.constants import MessageType
from src.events import PresenceBroadcastEvent, PresenceSyncEvent, SendMessageEvent


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


@event_serializer.register(SendMessageEvent)
def send_message_serializer(e):
    return {
        "type": MessageType.MESSAGE,
        "from": e.from_user_id,
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
