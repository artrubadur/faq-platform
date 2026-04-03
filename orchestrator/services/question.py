from loguru import logger
from sqlalchemy.exc import NoResultFound

from orchestrator.core.config import config
from orchestrator.core.requests import RerankCandidate
from orchestrator.db.models.question import Question
from orchestrator.integrations import EmbeddingProvider, RerankProvider
from orchestrator.repositories import QuestionsRepository
from shared.api.exceptions import BadGatewayError, ConflictError, NotFoundError
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


class QuestionsService:
    def __init__(
        self,
        repository: QuestionsRepository,
        embedding_provider: EmbeddingProvider,
        rerank_provider: RerankProvider | None,
        best_match_threshold: float,
        related_threshold: float,
    ):
        self.repository = repository
        self.embedding_provider = embedding_provider
        self.rerank_provider = rerank_provider
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

    async def _rerank(
        self, query: str, similar: list[Question], similarities: list[float]
    ):
        if self.rerank_provider is None:
            return similar

        candidates = [
            RerankCandidate(questions.id, questions.question_text, similarity)
            for questions, similarity in zip(similar, similarities)
        ]

        try:
            reranking = await self.rerank_provider.rerank(query, candidates)
        except Exception:
            logger.exception("Failed to re-rank similar questions ")
            return similar

        order = {qid: i for i, qid in enumerate(reranking)}
        return sorted(
            similar,
            key=lambda q: order.get(
                q.id, len(order)
            ),  # for IDs that are not in re-ranking for some re-ranker mistake
        )

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

    async def _get_most_popular_questions(
        self,
        amount: int,
        exclude_questions: list[Question] = [],
    ) -> list[Question]:
        if amount == 0:
            return []
        exclude_ids = [q.id for q in exclude_questions]
        return await self.repository.get_most_popular(amount, exclude_ids)

    async def get_popular_questions(
        self,
        amount: int,
    ) -> list[QuestionResponse]:
        questions = await self._get_most_popular_questions(amount)
        return [self._to_response(question) for question in questions]

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

        return questions, similarities

    def _build_similarity_map(
        self,
        questions: list[Question],
        similarities: list[float],
    ) -> dict[int, float]:
        return {
            question.id: similarity
            for question, similarity in zip(questions, similarities)
        }

    def _is_obvious_match(
        self,
        questions: list[Question],
        similarity_by_question_id: dict[int, float],
    ) -> bool:
        best_similarity = similarity_by_question_id[questions[0].id]
        second_similarity = (
            similarity_by_question_id[questions[1].id] if len(questions) > 1 else 0.0
        )

        if best_similarity >= 1 - 1e-6:
            return True

        return (
            best_similarity >= config.search.best_match_threshold - 1e-6
            and best_similarity - second_similarity >= config.search.obvious_margin
        )

    def _is_confident_match(
        self,
        questions: list[Question],
        similarity_by_question_id: dict[int, float],
    ) -> bool:
        best_similarity = similarity_by_question_id[questions[0].id]
        second_similarity = (
            similarity_by_question_id[questions[1].id] if len(questions) > 1 else 0.0
        )

        return (
            best_similarity >= config.search.best_match_threshold - 1e-6
            and best_similarity - second_similarity >= config.search.best_match_margin
        )

    async def _complite_with_popular_questions(
        self, questions: list[Question], max_popular_amount: int, max_amount: int
    ):
        popular_amount = min(max_amount - len(questions), max_popular_amount)

        popular = await self._get_most_popular_questions(
            popular_amount,
            questions,
        )

        return questions + popular

    def _calculate_rating_gain(
        self,
        best_similarity: float,
    ) -> float:
        threshold = config.search.best_match_threshold

        if best_similarity < threshold - 1e-6:
            return 0.0

        if threshold == 1:
            return 1.0

        norm = (best_similarity - threshold) / (1 - threshold)
        norm = max(0.0, norm)

        return norm**2

    async def suggest_questions(
        self,
        request: SuggestQuestionsRequest,
    ) -> QuestionSuggestionResponse:
        similar, similarities = await self._get_similar_questions(
            request.question_text,
            request.max_similar_amount + 1,
        )

        if not similar:
            popular = await self._get_most_popular_questions(request.max_popular_amount)
            return QuestionSuggestionResponse(
                questions=[self._to_response(q) for q in popular],
                is_confident=False,
            )

        similarity_by_question_id = self._build_similarity_map(similar, similarities)

        is_obvious = self._is_obvious_match(similar, similarity_by_question_id)

        if is_obvious:
            best_similarity = similarity_by_question_id[similar[0].id]
            gain = self._calculate_rating_gain(best_similarity)
            await self.repository.increment_ratings([similar[0]], [gain])

            suggestions = await self._complite_with_popular_questions(
                similar, request.max_popular_amount, request.max_amount
            )

            return QuestionSuggestionResponse(
                questions=[self._to_response(question) for question in suggestions],
                is_confident=True,
            )

        similar_reranked = await self._rerank(
            request.question_text,
            similar,
            similarities,
        )

        is_confident = self._is_confident_match(
            similar_reranked,
            similarity_by_question_id,
        )

        if is_confident:
            best_similarity = similarity_by_question_id[similar_reranked[0].id]
            gain = self._calculate_rating_gain(best_similarity)
            await self.repository.increment_ratings([similar_reranked[0]], [gain])
        elif len(similar_reranked) > request.max_similar_amount:
            similar_reranked = similar_reranked[:-1]

        suggestions = await self._complite_with_popular_questions(
            similar_reranked, request.max_popular_amount, request.max_amount
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
