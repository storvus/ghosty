from datetime import datetime, timezone

from sqlalchemy import TIMESTAMP, ForeignKey, String, func, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db import Base


class Message(Base):
    __tablename__ = "message"
    __table_args__ = (
        UniqueConstraint("client_message_id", "sender_id"),
        Index("ix_message_conversation_id_id", "conversation_id", "id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    client_message_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
    )
    sender_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True
    )
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversation.id", ondelete="CASCADE"), nullable=False
    )
    # ToDo: no removals for MVP
    # is_deleted: Mapped[bool] = mapped_column(
    #     Boolean, nullable=False, default=False, server_default=text("false")
    # )

    text: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )
    # ToDo: no edits for MVP
    # edited_at: Mapped[datetime | None] = mapped_column(
    #     TIMESTAMP(timezone=True),
    #     nullable=True,
    # )
