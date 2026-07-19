from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel

from src.aliases import UserId
from src.constants import MessageType, Presence


class IncomingEvent(BaseModel):
    type: MessageType


class IncomingMessageEvent(IncomingEvent):
    type: Literal["message"]
    conversation_id: int | None
    recipient_id: int | None
    client_message_id: str
    message: str
#
#
# class PresenceEvent(IncomingEvent):
#     type: Literal["presence"]
#     presence: Presence
#
#
# class HeartbeatEvent(IncomingEvent):
#     type: Literal["heartbeat"]
#
#
# class HelloEvent(IncomingEvent):
#     type: Literal["hello"]
#     presence: Presence
#
#
# @dataclass
# class OutgoingEvent:
#     pass
#
#
# @dataclass
# class OutgoingMessageEvent(OutgoingEvent):
#     from_uid: UserId
#     from_username: str
#     to_user_id: UserId
#     message: str
#
#
# @dataclass
# class PresenceSyncEvent(OutgoingEvent):
#     user_id: UserId
#     presence: Presence
#
#
# @dataclass
# class PresenceBroadcastEvent(OutgoingEvent):
#     subject_user_id: UserId
#     audience_user_ids: list[UserId]
#     presence: Presence
#
#
# @dataclass
# class ErrorEvent(OutgoingEvent):
#     user_id: UserId
#     error: str
#
#
# @dataclass
# class FriendAdded(OutgoingEvent): ...
#
#
# @dataclass
# class FriendRemoved(OutgoingEvent): ...
#
#
# @dataclass
# class InvisibleExceptionAdded(OutgoingEvent): ...
#
#
# @dataclass
# class InvisibleExceptionRemoved(OutgoingEvent): ...
