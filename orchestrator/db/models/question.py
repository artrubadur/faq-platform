from sqlalchemy import Float, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column

from orchestrator.core.config import config
from orchestrator.db.base import Base


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question_text: Mapped[str] = mapped_column(
        String(config.db_schema.question_text_max_len)
    )
    answer_text: Mapped[str] = mapped_column(
        String(config.db_schema.answer_text_max_len)
    )
    rating: Mapped[float] = mapped_column(Float, server_default=text("0.0"))
