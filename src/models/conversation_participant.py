from datetime import datetime

from sqlalchemy import ForeignKey, Index, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db import Base


class ConversationParticipant(Base):
    __tablename__ = "conversation_participant"
    __table_args__ = (
        Index("ix_participant_user", "user_id"),
    )

    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversation.id", ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), primary_key=True
    )
    joined_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    last_read_message_id: Mapped[int] = mapped_column(
        ForeignKey("message.id", ondelete="SET NULL"),
        nullable=True,
        default=None,
    )
