from enum import Enum
from typing import Tuple

from pgvector.sqlalchemy import Vector
from sqlalchemy import Row, cast, delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from orchestrator.core.config import config
from orchestrator.db.models import Alternative, Question


class AlternativeColumn(Enum):
    ID = "id"
    QUESTION_ID = "question_id"
    QUESTION_TEXT = "question_text"


class AlternativesRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        question_id: int,
        question_text: str,
        embedding: list[float],
    ) -> Alternative:
        alternative = Alternative(
            question_id=question_id,
            question_text=question_text,
            embedding=embedding,
        )
        self.session.add(alternative)
        await self.session.commit()
        await self.session.refresh(alternative)
        return alternative

    async def get_by_id(self, id: int) -> Alternative:
        result = await self.session.execute(
            select(Alternative).where(Alternative.id == id)
        )
        return result.scalar_one()

    async def get_slice(
        self,
        offset: int,
        limit: int,
        order_by: str,
        ascending: bool,
        *,
        question_id: int | None = None,
    ) -> list[Alternative]:
        col = getattr(Alternative, order_by)
        order_expr = col.asc() if ascending else col.desc()

        query = select(Alternative)
        if question_id is not None:
            query = query.where(Alternative.question_id == question_id)

        result = await self.session.execute(
            query.order_by(order_expr).offset(offset).limit(limit)
        )
        return list(result.scalars().all())

    async def get_amount(self, *, question_id: int | None = None) -> int:
        query = select(func.count()).select_from(Alternative)
        if question_id is not None:
            query = query.where(Alternative.question_id == question_id)

        amount = await self.session.execute(query)
        return int(amount.scalar() or 0)

    async def get_by_question_id(self, question_id: int) -> list[Alternative]:
        result = await self.session.execute(
            select(Alternative)
            .where(Alternative.question_id == question_id)
            .order_by(Alternative.id.asc())
        )
        return list(result.scalars().all())

    async def get_similar_main_questions(
        self,
        embedding: list[float],
        *,
        limit: int,
        max_distance: float = 1,
    ) -> list[Row[Tuple[Question, float]]]:
        embedding_vec = cast(embedding, Vector(config.db_schema.question_embedding_dim))
        distance = func.cosine_distance(Alternative.embedding, embedding_vec)
        similarity = 1 - distance

        pooled = (
            select(
                Alternative.question_id.label("question_id"),
                func.max(similarity).label("similarity"),
            )
            .where(distance <= max_distance)
            .group_by(Alternative.question_id)
            .subquery()
        )

        result = await self.session.execute(
            select(Question, pooled.c.similarity)
            .join(pooled, pooled.c.question_id == Question.id)
            .order_by(pooled.c.similarity.desc(), Question.id.asc())
            .limit(limit)
        )
        return list(result.all())

    async def update(self, id: int, **kwargs) -> Alternative:
        result = await self.session.execute(
            update(Alternative)
            .where(Alternative.id == id)
            .values(**kwargs)
            .returning(Alternative)
        )
        await self.session.commit()
        return result.scalar_one()

    async def delete(self, id: int) -> Alternative:
        result = await self.session.execute(
            delete(Alternative).where(Alternative.id == id).returning(Alternative)
        )
        await self.session.commit()
        return result.scalar_one()
