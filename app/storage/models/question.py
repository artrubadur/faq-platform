from pgvector.sqlalchemy import Vector
from sqlalchemy import Float, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.storage.base import Base


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question_text: Mapped[str] = mapped_column(String(384))
    answer_text: Mapped[str] = mapped_column(String(384))
    rating: Mapped[float] = mapped_column(Float, server_default=text("0.0"))
    embedding: Mapped[list[float]] = mapped_column(Vector(256))
