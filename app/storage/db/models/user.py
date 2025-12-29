from enum import Enum

from sqlalchemy import BigInteger, String
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column

from app.storage.db.base import Base


class Role(str, Enum):
    BANNED = "banned"
    USER = "user"
    RESPONDER = "responder"
    HR = "hr"
    MODERATOR = "moderator"
    ADMIN = "admin"


role_enum = ENUM(*Role, name="role_enum")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int | None] = mapped_column(BigInteger, unique=True)
    username: Mapped[str | None] = mapped_column(
        String(32), unique=True, nullable=False
    )
    role: Mapped[str] = mapped_column(role_enum, nullable=False)
