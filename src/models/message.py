# from datetime import datetime, timezone
#
# from sqlalchemy import TIMESTAMP, Boolean, ForeignKey, String, func, text, UniqueConstraint
# from sqlalchemy.orm import Mapped, mapped_column
#
# from src.core.db import Base
#
#
# class Message(Base):
#     __tablename__ = "message"
#     __table_args__ = (
#         UniqueConstraint("client_message_id", "sender_id"),
#     )
#
#     id: Mapped[int] = mapped_column(primary_key=True)
#     client_message_id: Mapped[str] = mapped_column(
#         String(36),
#         nullable=False,
#         index=True,
#     )
#
#     sender_id: Mapped[int] = mapped_column(
#         ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True
#     )
#     conversation_id: Mapped[int] = mapped_column(
#         ForeignKey("conversation.id", ondelete="CASCADE"), nullable=False, index=True
#     )
#     deleted: Mapped[bool] = mapped_column(
#         Boolean, nullable=False, default=False, server_default=text("false")
#     )
#
#     text: Mapped[str] = mapped_column(String, nullable=False)
#     created_at: Mapped[datetime] = mapped_column(
#         TIMESTAMP(timezone=True),
#         nullable=False,
#         default=lambda: datetime.now(timezone.utc),
#         server_default=func.now(),
#     )
#     edited_at: Mapped[datetime | None] = mapped_column(
#         TIMESTAMP(timezone=True),
#         nullable=True,
#     )
