from datetime import datetime, timezone

from sqlalchemy import TIMESTAMP, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db import Base

from sqlalchemy import Enum
import enum

class ConversationType(str, enum.Enum):
    direct = "direct"
    group = "group"  # на будущее


class Conversation(Base):
    __tablename__ = "conversation"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[ConversationType] = mapped_column(
        Enum(ConversationType),
        nullable=False,
        default=ConversationType.direct,
    )
    conversation_key: Mapped[str] = mapped_column(
        String,
        nullable=False,
        unique=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )
