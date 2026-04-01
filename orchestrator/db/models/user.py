from sqlalchemy import BigInteger, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from orchestrator.db.base import Base
from shared.contracts.user.responses import Role


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(
        String(32), unique=True, nullable=True, index=True
    )
    role: Mapped[Role] = mapped_column(String, index=True)
