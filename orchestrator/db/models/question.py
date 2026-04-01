from pgvector.sqlalchemy import Vector
from sqlalchemy import Float, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column

from orchestrator.core.config import config
from orchestrator.db.base import Base


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question_text: Mapped[str] = mapped_column(
        String(config.db_schema.max_question_text_len)
    )
    answer_text: Mapped[str] = mapped_column(
        String(config.db_schema.max_answer_text_len)
    )
    rating: Mapped[float] = mapped_column(Float, server_default=text("0.0"))
    embedding: Mapped[list[float]] = mapped_column(
        Vector(config.db_schema.embedding_dim)
    )
