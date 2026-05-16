from sqlalchemy import BigInteger, ForeignKey, Identity, String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db import Base


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    display_number: Mapped[int] = mapped_column(
        BigInteger, Identity(start=10000, increment=1), unique=True, nullable=False
    )


class UserSubscription(Base):
    __tablename__ = "user_subscription"

    subscriber_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
        index=True,
    )
    target_user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
        index=True,
    )
