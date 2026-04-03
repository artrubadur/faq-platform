from loguru import logger
from sqlalchemy.exc import NoResultFound

from orchestrator.core.config import config
from orchestrator.core.requests import ComposeCandidate, RerankCandidate
from orchestrator.db.models.question import Question
from orchestrator.integrations import ComposeProvider, EmbeddingProvider, RerankProvider
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
        compose_provider: ComposeProvider | None,
        best_match_threshold: float,
        related_threshold: float,
    ):
        self.repository = repository
        self.embedding_provider = embedding_provider
        self.rerank_provider = rerank_provider
        self.compose_provider = compose_provider
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

    async def _complete_with_popular_questions(
        self, questions: list[Question], max_popular_amount: int, max_amount: int
    ):
        popular_amount = min(max_amount - len(questions), max_popular_amount)

        popular = await self._get_most_popular_questions(
            popular_amount,
            questions,
        )

        return questions + popular

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
            best_similarity >= config.suggestion.search.best_match_threshold - 1e-6
            and best_similarity - second_similarity
            >= config.suggestion.search.obvious_margin
        )

    async def _rerank(
        self,
        query: str,
        questions: list[Question],
        similarity_by_question_id: dict[int, float],
    ):
        if self.rerank_provider is None:
            return questions

        candidates = [
            RerankCandidate(q.id, q.question_text, similarity_by_question_id[q.id])
            for q in questions
        ]

        try:
            reranking = await self.rerank_provider.rerank(query, candidates)
        except Exception:
            logger.exception(
                "Failed to rerank similar questions",
            )
            return questions

        order = {qid: i for i, qid in enumerate(reranking)}
        logger.debug(
            "Rerank applied",
        )
        return sorted(
            questions,
            key=lambda q: order.get(
                q.id, len(order)
            ),  # for IDs that are not in re-ranking for some re-ranker mistake
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
            best_similarity >= config.suggestion.search.best_match_threshold - 1e-6
            and best_similarity - second_similarity
            >= config.suggestion.search.best_match_margin
        )

    async def _compose(
        self,
        query: str,
        questions: list[Question],
        similarity_by_question_id: dict[int, float],
    ) -> str:
        if self.compose_provider is None:
            return questions[0].answer_text

        best_candidate = ComposeCandidate(
            questions[0].question_text,
            questions[0].answer_text,
        )
        supporting_threshold = (
            similarity_by_question_id[questions[0].id]
            - config.suggestion.compose.supporting_margin
        )

        supporting_candidates = [
            ComposeCandidate(q.question_text, q.answer_text)
            for q in questions[1 : 1 + config.suggestion.compose.supporting_top_k]
            if similarity_by_question_id[q.id] >= supporting_threshold
        ]

        try:
            composition = await self.compose_provider.compose(
                query, best_candidate, supporting_candidates
            )
        except Exception:
            logger.exception("Failed to compose similar questions")
            return questions[0].answer_text

        logger.debug(
            "Compose applied",
        )
        return composition

    def _calculate_rating_gain(
        self,
        best_similarity: float,
    ) -> float:
        threshold = config.suggestion.search.best_match_threshold

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
            logger.debug(
                "No similar questions found, returning popular questions only: popular_count={popular_count}",
                popular_count=len(popular),
            )
            return QuestionSuggestionResponse(
                questions=[self._to_response(q) for q in popular],
                is_confident=False,
            )

        similarity_by_question_id = self._build_similarity_map(similar, similarities)

        is_obvious = self._is_obvious_match(similar, similarity_by_question_id)

        if is_obvious:
            best_similarity = similarity_by_question_id[similar[0].id]
            logger.debug(
                "Obvious similar question found: id={question_id}, similarity={similarity}",
                question_id=similar[0].id,
                similarity=best_similarity,
            )
            gain = self._calculate_rating_gain(best_similarity)
            await self.repository.increment_ratings([similar[0]], [gain])

            suggestions = await self._complete_with_popular_questions(
                similar[:request.max_similar_amount], request.max_popular_amount, request.max_amount
            )

            return QuestionSuggestionResponse(
                questions=[self._to_response(question) for question in suggestions],
                is_confident=True,
            )

        similar_reranked = await self._rerank(
            request.question_text,
            similar,
            similarity_by_question_id,
        )

        is_confident = self._is_confident_match(
            similar_reranked,
            similarity_by_question_id,
        )

        if is_confident:
            best_similarity = similarity_by_question_id[similar_reranked[0].id]
            logger.debug(
                "Confident similar question found: id={question_id}, similarity={similarity}",
                question_id=similar_reranked[0].id,
                similarity=best_similarity,
            )
            gain = self._calculate_rating_gain(best_similarity)
            await self.repository.increment_ratings([similar_reranked[0]], [gain])

            similar_reranked[0].answer_text = await self._compose(
                request.question_text, similar_reranked, similarity_by_question_id
            )
        else:
            similar_reranked = similar_reranked[:request.max_similar_amount]

        suggestions = await self._complete_with_popular_questions(
            similar_reranked, request.max_popular_amount, request.max_amount
        )
        return QuestionSuggestionResponse(
            questions=[self._to_response(question) for question in suggestions],
            is_confident=is_confident,
        )
