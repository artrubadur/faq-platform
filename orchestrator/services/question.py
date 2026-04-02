from loguru import logger
from sqlalchemy.exc import NoResultFound

from orchestrator.core.config import config
from orchestrator.db.models.question import Question
from orchestrator.integrations.embedding.provider import EmbeddingProvider
from orchestrator.repositories import QuestionsRepository
from shared.contracts.question.requests import (
    CreateQuestionRequest,
    ListQuestionsRequest,
    SuggestQuestionsRequest,
    UpdateQuestionRequest,
)
from shared.contracts.question.responses import (
    QuestionResponse,
    QuestionsAmountResponse,
    QuestionSuggestionResponse,
)
from shared.http.exceptions import BadGatewayError, ConflictError, NotFoundError


class QuestionsService:
    def __init__(
        self,
        repository: QuestionsRepository,
        embedding_provider: EmbeddingProvider,
        best_match_threshold: float,
        related_threshold: float,
    ):
        self.repository = repository
        self.embedding_provider = embedding_provider
        self.best_match_distance = 1 - best_match_threshold
        self.related_distance = 1 - related_threshold

    def _to_response(self, question: Question) -> QuestionResponse:
        return QuestionResponse.model_validate(question)

    async def _compute_embedding(self, text: str) -> list[float]:
        try:
            return await self.embedding_provider.compute_embedding(text)
        except Exception as exc:
            logger.exception("Failed to compute the question embedding")
            raise BadGatewayError("Failed to compute the question embedding") from exc

    async def _get_existing_question(self, id: int) -> Question:
        try:
            return await self.repository.get_by_id(id)
        except NoResultFound as exc:
            raise NotFoundError(f"Question {id} not found") from exc

    async def create_question(self, request: CreateQuestionRequest) -> QuestionResponse:
        embedding = await self._compute_embedding(request.question_text)

        if request.check_similarity:
            rows = await self.repository.get_similar(
                embedding=embedding,
                limit=1,
                max_distance=self.best_match_distance,
            )
            if len(rows) > 0:
                similar, _ = rows[0]
                similar: Question
                raise ConflictError(
                    "A similar question already exists",
                    {"id": similar.id, "question_text": similar.question_text},
                )

        question = await self.repository.create(
            request.question_text,
            request.answer_text,
            embedding,
        )
        return self._to_response(question)

    async def get_question(self, id: int) -> QuestionResponse:
        question = await self._get_existing_question(id)
        return self._to_response(question)

    async def get_questions_amount(self) -> QuestionsAmountResponse:
        amount = await self.repository.get_amount()
        return QuestionsAmountResponse(amount=amount)

    async def get_paginated_questions(
        self,
        request: ListQuestionsRequest,
    ) -> list[QuestionResponse]:
        offset = (request.page - 1) * request.page_size
        questions = await self.repository.get_slice(
            offset, request.page_size, request.order_by, request.ascending
        )
        return [self._to_response(question) for question in questions]

    async def delete_question(self, id: int) -> QuestionResponse:
        try:
            question = await self.repository.delete(id)
        except NoResultFound as exc:
            raise NotFoundError(f"Question {id} not found") from exc
        return self._to_response(question)

    async def _get_similar_questions(
        self,
        question_text: str,
        amount: int,
    ) -> tuple[list[Question], list[float]]:
        embedding = await self._compute_embedding(question_text)
        rows = await self.repository.get_similar(
            embedding=embedding,
            limit=amount,
            max_distance=self.related_distance,
        )

        questions: list[Question] = [row[0] for row in rows]
        similarities: list[float] = [1 - row[1] for row in rows]

        if similarities:
            sim1 = similarities[0]
            sim2 = similarities[1] if len(similarities) > 1 else 0.0
            threshold = config.search.best_match_threshold

            if (
                sim1 >= threshold - 1e-6
            ):  # Handle floating-point precision issues for threshold == 1
                if threshold == 1:
                    await self.repository.increment_ratings([questions[0]], [1.0])
                else:
                    norm = (sim1 - threshold) / (1 - threshold)
                    norm = max(0.0, min(norm, 1.0))

                    gap = (sim1 - sim2) * 10
                    gap = max(0.0, min(gap, 1.0))

                    gain = norm**2 * gap

                    if gain > 0:
                        await self.repository.increment_ratings([questions[0]], [gain])

        return questions, similarities

    async def _get_most_popular_questions(
        self,
        amount: int,
        exclude_questions: list[Question] | None = None,
    ) -> list[Question]:
        exclude_ids = [q.id for q in (exclude_questions or [])]
        return await self.repository.get_most_popular(amount, exclude_ids)

    async def get_popular_questions(
        self,
        amount: int,
    ) -> list[QuestionResponse]:
        questions = await self._get_most_popular_questions(amount)
        return [self._to_response(question) for question in questions]

    async def suggest_questions(
        self,
        request: SuggestQuestionsRequest,
    ) -> QuestionSuggestionResponse:
        similar, similarities = await self._get_similar_questions(
            request.question_text,
            request.max_similar_amount + 1,
        )

        popular_amount = max(
            0,
            min(request.max_amount - len(similar), request.max_popular_amount),
        )
        popular = await self._get_most_popular_questions(popular_amount, similar)
        suggestions = (similar + popular)[: request.max_amount]
        is_confident = (
            len(similarities) != 0
            and similarities[0] >= config.search.best_match_threshold
        )

        return QuestionSuggestionResponse(
            questions=[self._to_response(question) for question in suggestions],
            is_confident=is_confident,
        )

    async def update_question(
        self,
        id: int,
        request: UpdateQuestionRequest,
    ) -> QuestionResponse:
        existing = await self._get_existing_question(id)

        update_fields: dict = {}
        if request.question_text is not None:
            update_fields["question_text"] = request.question_text
        if request.answer_text is not None:
            update_fields["answer_text"] = request.answer_text
        if request.rating is not None:
            update_fields["rating"] = request.rating

        if request.recompute_embedding:
            question_text = request.question_text or existing.question_text
            update_fields["embedding"] = await self._compute_embedding(question_text)

        if not update_fields:
            return self._to_response(existing)

        try:
            question = await self.repository.update(id, **update_fields)
        except NoResultFound as exc:
            raise NotFoundError(f"Question {id} not found") from exc
        return self._to_response(question)
