from enum import Enum


class Presence(str, Enum):
    AWAY = "away"
    DO_NOT_DISTURB = "do_not_disturb"
    ONLINE = "online"
    INVISIBLE = "invisible"
    INVISIBLE_EXCEPT = "invisible_except"
    OFFLINE = "offline"


class ConnectionState:
    CONNECTED = "connected"
    AUTHENTICATED = "authenticated"
    HELLO_RECEIVED = "hello_received"
    ACTIVE = "active"
    CLOSED = "closed"


class MessageType(str, Enum):
    NEW_PRESENCE = "update_presence"
    NOTIFY_PRESENCE = "notify_presence"
    SYNC_PRESENCE = "sync_presence"
    MESSAGE = "message"
    HEARTBEAT = "heartbeat"
