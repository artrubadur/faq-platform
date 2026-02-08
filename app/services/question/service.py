from app.core.exceptions import SimilarityError
from app.repositories import QuestionsRepository
from app.services.question.embedding import EmbeddingService, embedding_service
from app.storage.models import Question
from app.core.config import config


class QuestionsService:
    def __init__(
        self,
        repository: QuestionsRepository,
        max_distance: float | None = None,
        new_embedding_service: EmbeddingService | None = None,
    ):
        self.repository = repository
        self.max_distance = max_distance or (1 - config.qn_sim_threshold)
        self.embedding_service = new_embedding_service or embedding_service

    async def create_question(
        self, question_text: str, question_answer: str, check_similarity: bool
    ) -> Question:
        embedding = await self.embedding_service.compute(question_text)

        if check_similarity:
            row = await self.repository.get_similar(
                embedding=embedding, limit=1, max_distance=self.max_distance
            )
            if len(row) > 0:
                similar, distance = row[0]
                similarity = 1 - distance
                raise SimilarityError(
                    "A similar question already exists", similar, similarity
                )

        return await self.repository.create(
            question_text,
            question_answer,
            embedding,
        )

    async def get_question(self, id: int) -> Question:
        return await self.repository.get_by_id(id)

    async def get_most_popular_questions(
        self, amount: int, exclude_questions: list[Question] = []
    ) -> list[Question]:
        exclude_ids = [q.id for q in exclude_questions]
        questions = await self.repository.get_most_popular(amount, exclude_ids)
        return list(questions)

    async def get_questions_amount(self) -> int:
        return await self.repository.get_amount()

    async def get_paginated_questions(
        self, page: int, page_size: int, order_by: str, ascending: bool
    ) -> list[Question]:
        offset = (page - 1) * page_size
        questions = await self.repository.get_slice(
            offset, page_size, order_by, ascending
        )
        return list(questions)

    async def delete_question(self, id: int) -> Question:
        return await self.repository.delete(id)

    async def get_similar_questions(
        self,
        question_text: str,
        amount: int,
    ) -> tuple[list[Question], list[float]]:
        embedding = await self.embedding_service.compute(question_text)
        rows = await self.repository.get_similar(
            embedding=embedding, limit=amount, max_distance=0.2
        )
        questions: list[Question] = [row[0] for row in rows]
        similarities: list[float] = [1 - row[1] for row in rows]

        await self.repository.increment_ratings(questions, similarities)
        return questions, similarities

    async def update_question(
        self,
        id: int,
        question_text: str,
        answer_text: str,
        rating: float,
        recompute_embedding: bool,
    ) -> Question:
        update_fields: dict = {
            "question_text": question_text,
            "answer_text": answer_text,
            "rating": rating,
        }

        if recompute_embedding:
            update_fields["embedding"] = await self.embedding_service.compute(
                question_text
            )

        return await self.repository.update(id, **update_fields)
