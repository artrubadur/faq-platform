from loguru import logger
from sqlalchemy.exc import NoResultFound

from orchestrator.integrations import EmbeddingProvider
from orchestrator.repositories import FormulationsRepository, QuestionsRepository
from shared.api.exceptions import BadGatewayError, NotFoundError
from shared.contracts.formulation.requests import (
    CreateFormulationRequest,
    ListFormulationsRequest,
    UpdateFormulationRequest,
)
from shared.contracts.formulation.responses import (
    FormulationResponse,
    FormulationsAmountResponse,
)


class FormulationsService:
    def __init__(
        self,
        repository: FormulationsRepository,
        questions_repository: QuestionsRepository,
        embedding_provider: EmbeddingProvider,
    ):
        self.repository = repository
        self.questions_repository = questions_repository
        self.embedding_provider = embedding_provider

    def _to_response(
        self,
        formulation,
    ) -> FormulationResponse:
        return FormulationResponse.model_validate(formulation)

    async def _compute_embedding(self, text: str) -> list[float]:
        try:
            return await self.embedding_provider.compute_embedding(text)
        except Exception as exc:
            logger.exception("Failed to compute the question embedding")
            raise BadGatewayError("Failed to compute the question embedding") from exc

    async def _ensure_main_question_exists(self, question_id: int) -> None:
        try:
            await self.questions_repository.get_by_id(question_id)
        except NoResultFound as exc:
            raise NotFoundError(f"Question {question_id} not found") from exc

    async def _get_existing_formulation(self, id: int):
        try:
            return await self.repository.get_by_id(id)
        except NoResultFound as exc:
            raise NotFoundError(f"Formulation {id} not found") from exc

    async def create_formulation(
        self,
        request: CreateFormulationRequest,
    ) -> FormulationResponse:
        await self._ensure_main_question_exists(request.question_id)
        embedding = await self._compute_embedding(request.question_text)
        formulation = await self.repository.create(
            request.question_id,
            request.question_text,
            embedding,
        )
        return self._to_response(formulation)

    async def get_formulation(self, id: int) -> FormulationResponse:
        formulation = await self._get_existing_formulation(id)
        return self._to_response(formulation)

    async def get_formulations_amount(
        self,
        question_id: int | None,
    ) -> FormulationsAmountResponse:
        if question_id is not None:
            await self._ensure_main_question_exists(question_id)

        amount = await self.repository.get_amount(question_id=question_id)
        return FormulationsAmountResponse(amount=amount)

    async def get_paginated_formulations(
        self,
        request: ListFormulationsRequest,
    ) -> list[FormulationResponse]:
        if request.question_id is not None:
            await self._ensure_main_question_exists(request.question_id)

        offset = (request.page - 1) * request.page_size
        formulations = await self.repository.get_slice(
            offset,
            request.page_size,
            request.order_by,
            request.ascending,
            question_id=request.question_id,
        )
        return [self._to_response(item) for item in formulations]

    async def update_formulation(
        self,
        id: int,
        request: UpdateFormulationRequest,
    ) -> FormulationResponse:
        existing = await self._get_existing_formulation(id)

        update_fields: dict = {}
        if (
            request.question_id is not None
            and request.question_id != existing.question_id
        ):
            await self._ensure_main_question_exists(request.question_id)
            update_fields["question_id"] = request.question_id

        if request.question_text is not None:
            update_fields["question_text"] = request.question_text
            if request.recompute_embedding:
                update_fields["embedding"] = await self._compute_embedding(
                    request.question_text
                )

        if not update_fields:
            return self._to_response(existing)

        try:
            formulation = await self.repository.update(id, **update_fields)
        except NoResultFound as exc:
            raise NotFoundError(f"Formulation {id} not found") from exc
        return self._to_response(formulation)

    async def delete_formulation(
        self,
        id: int,
    ) -> FormulationResponse:
        try:
            formulation = await self.repository.delete(id)
        except NoResultFound as exc:
            raise NotFoundError(f"Formulation {id} not found") from exc
        return self._to_response(formulation)
