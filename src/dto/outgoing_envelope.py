from dataclasses import dataclass, field
from typing import Any


@dataclass
class OutgoingEnvelope:
    payload: dict[str, Any]
    user_ids: list[int] = field(default_factory=list)
    connection_ids: list[str] = field(default_factory=list)
