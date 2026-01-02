from enum import Enum
from numpy import ndarray
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.storage.db.models import Question
from typing import cast

from sqlalchemy import func, select

class QuestionColumn(Enum):
    ID = "id"
    QUESTION_TEXT = "question_text"
    ANSWER_TEXT = "answer_text"
    EMBEDDING = "embedding"

class QuestionsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self, question_text: str, answer_text: str, embedding: ndarray
    ) -> Question:
        new_question = Question(
            question_text=question_text, answer_text=answer_text, embedding=embedding
        )
        self.session.add(new_question)
        await self.session.commit()
        await self.session.refresh(new_question)
        return new_question

    async def get(self, id: int) -> Question:
        question = await self.session.execute(select(Question).where(Question.id == id))
        return question.scalar_one()

    async def get_slice(self, offset: int, limit: int, order_by: str, ascending: bool):
        col = getattr(Question, order_by)

        order_expr = col.asc() if ascending else col.desc()

        result = await self.session.execute(
            select(Question).order_by(order_expr).offset(offset).limit(limit)
        )
        return result.scalars().all()

    async def get_amount(self) -> int:
        count = cast(
            int, await self.session.scalar(select(func.count()).select_from(Question))
        )
        return count

    async def update(self, id: int, **kwargs) -> Question:
        question = await self.get(id)
        for key, value in kwargs.items():
            setattr(question, key, value)
        await self.session.commit()
        return question

    async def delete(self, id: int):
        question = await self.get(id)
        await self.session.delete(question)
        await self.session.commit()
        return question
