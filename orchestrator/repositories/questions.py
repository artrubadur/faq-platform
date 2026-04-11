from enum import Enum
from typing import cast as type_cast

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from orchestrator.db.models import Question


class QuestionColumn(Enum):
    ID = "id"
    RATING = "rating"
    QUESTION_TEXT = "question_text"
    ANSWER_TEXT = "answer_text"


class QuestionsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, question_text: str, answer_text: str) -> Question:
        new_question = Question(question_text=question_text, answer_text=answer_text)
        self.session.add(new_question)
        await self.session.commit()
        await self.session.refresh(new_question)
        return new_question

    async def get_by_id(self, id: int) -> Question:
        question = await self.session.execute(select(Question).where(Question.id == id))
        return question.scalar_one()

    async def get_most_popular(
        self, limit: int, exclude_ids: list[int]
    ) -> list[Question]:
        questions = await self.session.execute(
            select(Question)
            .where(Question.id.notin_(exclude_ids))
            .order_by(Question.rating.desc())
            .limit(limit)
        )
        return list(questions.scalars().all())

    async def get_slice(
        self, offset: int, limit: int, order_by: str, ascending: bool
    ) -> list[Question]:
        col = getattr(Question, order_by)

        order_expr = col.asc() if ascending else col.desc()

        questions = await self.session.execute(
            select(Question).order_by(order_expr).offset(offset).limit(limit)
        )
        return list(questions.scalars().all())

    async def get_amount(self) -> int:
        amount = await self.session.execute(select(func.count()).select_from(Question))
        return type_cast(int, amount.scalar())

    async def update(self, id: int, **kwargs) -> Question:
        result = await self.session.execute(
            update(Question)
            .where(Question.id == id)
            .values(**kwargs)
            .returning(Question)
        )
        await self.session.commit()
        return result.scalar_one()

    async def increment_ratings(
        self, questions: list[Question], similarities: list[float]
    ):
        for question, similarity in zip(questions, similarities):
            question.rating += similarity
        await self.session.commit()

    async def delete(self, id: int) -> Question:
        result = await self.session.execute(
            delete(Question).where(Question.id == id).returning(Question)
        )
        await self.session.commit()
        return result.scalar_one()
