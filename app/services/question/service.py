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
    ) -> Question: # TODO: THE CHECK OF THE SIMILARITY WITH EXISTING QUSTIONS
        embedding = embedding_computer(question_text)

        if check_similarity and (similar_id := find_similar(embedding)) is not None:
            similar_question = await self.read_question(similar_id)
            raise SimilarityError("A similar question already exists", similar_question)

        return await self.repository.create( # TODO: EXCEPTION HANDLING
            question_text,
            question_answer,
            embedding,
        )
        

    async def read_question(self, id: int) -> Question:
        return await self.repository.read(id)

    async def delete_question(self, id: int) -> Question:
        return await self.repository.delete(id)

    async def update_question(
        self,
        id: int,
        question_text: str | None,
        question_answer: str | None,
        recompute_embedding: bool,
    ) -> Question:
        update_fields = {}

        if question_text is not None:
            update_fields["question_text"] = question_text

            if recompute_embedding:
                update_fields["embedding"] = embedding_computer(question_text)
        else:
            if recompute_embedding:
                raise ValueError("Cannot recompute embedding without question_text.")

        if question_answer is not None:
            update_fields["question_text"] = question_answer

        return await self.repository.update(id, **update_fields)
