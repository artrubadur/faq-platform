import numpy as np

from app.core.exceptions import SimilarityError
from app.repositories import QuestionsRepository
from app.storage.db.models import Question


def embedding_computer(question_text: str):  # TODO: API REQUEST
    return np.random.rand(1024)


def find_similar(embedding: np.ndarray) -> int | None:  # TODO: API REQUEST
    return None


class QuestionsService:
    def __init__(self, repository: QuestionsRepository):
        self.repository = repository

    async def create_question(
        self, question_text: str, question_answer: str, check_similarity: bool
    ) -> Question:  # TODO: THE CHECK OF THE SIMILARITY WITH EXISTING QUSTIONS
        embedding = embedding_computer(question_text)

        if check_similarity and (similar_id := find_similar(embedding)) is not None:
            similar_question = await self.get_question(similar_id)
            raise SimilarityError("A similar question already exists", similar_question)

        return await self.repository.create(  # TODO: EXCEPTION HANDLING
            question_text,
            question_answer,
            embedding,
        )

    async def get_question(self, id: int) -> Question:
        return await self.repository.get(id)

    async def get_questions_amount(self) -> int:
        return await self.repository.get_amount()

    async def get_paginated_questions(
        self, page: int, page_size: int, order_by: str, ascending: bool
    ) -> list[Question]:
        offset = (page - 1) * page_size
        questions = await self.repository.get_slice(offset, page_size, order_by, ascending)
        return list(questions)
    
    async def delete_question(self, id: int) -> Question:
        return await self.repository.delete(id)

    async def update_question(
        self,
        id: int,
        question_text: str,
        answer_text: str,
        recompute_embedding: bool,
    ) -> Question:
        update_fields: dict = {
            "question_text": question_text,
            "answer_text": answer_text,
        }

        if recompute_embedding:
            update_fields["embedding"] = embedding_computer(question_text)

        return await self.repository.update(id, **update_fields)
