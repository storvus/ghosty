from typing import Annotated

from pydantic import Field, TypeAdapter

from src.events import IncomingMessageEvent

# ToDo - more events: typing? marked as read?
Event = Annotated[
    IncomingMessageEvent,
    # | PresenceEvent | HeartbeatEvent | HelloEvent,
    Field(discriminator="type"),
]

EVENT_ADAPTER = TypeAdapter(Event)


def parse_event(
    data: dict,
) -> IncomingMessageEvent: # | PresenceEvent | HeartbeatEvent | HelloEvent:
    return EVENT_ADAPTER.validate_python(data)
