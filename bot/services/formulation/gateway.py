from bot.services.http_client import orchestrator_client
from shared.api.client import ApiClient
from shared.contracts.formulation.requests import (
    CreateFormulationRequest,
    FormulationFields,
    ListFormulationsRequest,
    UpdateFormulationRequest,
)
from shared.contracts.formulation.responses import (
    FormulationResponse,
    FormulationsAmountResponse,
)


class FormulationGateway:
    def __init__(
        self,
        client: ApiClient,
    ) -> None:
        self.client = client

    async def get_formulation(self, id: int) -> FormulationResponse:
        data = await self.client.get(f"/formulations/{id}")
        return FormulationResponse.model_validate(data)

    async def create_formulation(
        self,
        question_id: int,
        question_text: str,
    ) -> FormulationResponse:
        request = CreateFormulationRequest(
            question_id=question_id,
            question_text=question_text,
        )
        data = await self.client.post(
            "/formulations",
            json_data=request.model_dump(mode="json"),
        )
        return FormulationResponse.model_validate(data)

    async def update_formulation(
        self,
        id: int,
        question_id: int | None = None,
        question_text: str | None = None,
        recompute_embedding: bool | None = None,
    ) -> FormulationResponse:
        request = UpdateFormulationRequest(
            question_id=question_id,
            question_text=question_text,
            recompute_embedding=recompute_embedding,
        )
        data = await self.client.patch(
            f"/formulations/{id}",
            json_data=request.model_dump(
                mode="json",
                exclude_unset=True,
                exclude_none=True,
            ),
        )
        return FormulationResponse.model_validate(data)

    async def get_formulations_amount(self, question_id: int | None = None) -> int:
        params = {"question_id": question_id} if question_id is not None else None
        data = await self.client.get("/formulations/count", params=params)
        return FormulationsAmountResponse.model_validate(data).amount

    async def get_paginated_formulations(
        self,
        page: int,
        page_size: int,
        order_by: FormulationFields,
        ascending: bool,
        question_id: int | None = None,
    ) -> list[FormulationResponse]:
        request = ListFormulationsRequest(
            page=page,
            page_size=page_size,
            order_by=order_by,
            ascending=ascending,
            question_id=question_id,
        )
        data = await self.client.get(
            "/formulations",
            params=request.model_dump(mode="json", exclude_none=True),
        )
        return [FormulationResponse.model_validate(item) for item in data]

    async def delete_formulation(self, id: int) -> FormulationResponse:
        data = await self.client.delete(f"/formulations/{id}")
        return FormulationResponse.model_validate(data)


formulation_gateway = FormulationGateway(orchestrator_client)
