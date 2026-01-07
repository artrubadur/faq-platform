from enum import Enum

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from app.storage.base import Base


class Role(str, Enum):
    BANNED = "banned"
    USER = "user"
    RESPONDER = "responder"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int | None] = mapped_column(BigInteger, unique=True)
    username: Mapped[str | None] = mapped_column(
        String(32), unique=True, nullable=False
    )
    role: Mapped[Role] = mapped_column(String, nullable=False)
