import numpy as np
from pgvector.sqlalchemy import Vector
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.storage.db.base import Base


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    question: Mapped[str] = mapped_column(String(384))
    answer: Mapped[str] = mapped_column(String(384))
    embedding: Mapped[np.ndarray] = mapped_column(Vector(1024))
