from typing import Annotated

from pydantic import Field, TypeAdapter

from src.events import HeartbeatEvent, HelloEvent, MessageEvent, PresenceEvent

# ToDo: typing? marked as read?
Event = Annotated[MessageEvent | PresenceEvent | HeartbeatEvent | HelloEvent, Field(discriminator="type")]

EVENT_ADAPTER = TypeAdapter(Event)


def parse_event(data: dict) -> MessageEvent | PresenceEvent | HeartbeatEvent | HelloEvent:
    return EVENT_ADAPTER.validate_python(data)
