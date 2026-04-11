from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from orchestrator.core.config import config
from orchestrator.db.base import Base


class Formulation(Base):
    __tablename__ = "formulations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"),
        index=True,
    )
    question_text: Mapped[str] = mapped_column(
        String(config.db_schema.question_text_max_len)
    )
    embedding: Mapped[list[float]] = mapped_column(
        Vector(config.db_schema.question_embedding_dim)
    )
