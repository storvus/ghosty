from sqlalchemy import BigInteger, ForeignKey, Identity, String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db import Base


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(60), nullable=False)
    display_number: Mapped[int] = mapped_column(
        BigInteger, Identity(start=10000, increment=1), unique=True, nullable=False
    )

    @classmethod
    def create(cls, username: str, password_hash: str):
        return cls(
            username=username,
            password_hash=password_hash,
        )
