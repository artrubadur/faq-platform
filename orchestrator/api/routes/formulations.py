from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from orchestrator.api.dependencies import FormulationsServiceDep
from shared.contracts.formulation.requests import (
    CreateFormulationRequest,
    ListFormulationsRequest,
    UpdateFormulationRequest,
)
from shared.contracts.formulation.responses import (
    FormulationResponse,
    FormulationsAmountResponse,
)

router = APIRouter(
    prefix="/formulations",
    tags=["formulations"],
)


@router.post("", response_model=FormulationResponse)
async def create_formulation(
    request: CreateFormulationRequest,
    service: FormulationsServiceDep,
) -> FormulationResponse:
    return await service.create_formulation(request)


@router.get("/count", response_model=FormulationsAmountResponse)
async def get_formulations_amount(
    *,
    question_id: Annotated[int | None, Query(ge=1)] = None,
    service: FormulationsServiceDep,
) -> FormulationsAmountResponse:
    return await service.get_formulations_amount(question_id)


@router.get("", response_model=list[FormulationResponse])
async def get_paginated_formulations(
    request: Annotated[ListFormulationsRequest, Depends()],
    service: FormulationsServiceDep,
) -> list[FormulationResponse]:
    return await service.get_paginated_formulations(request)


@router.get("/{formulation_id}", response_model=FormulationResponse)
async def get_formulation(
    formulation_id: Annotated[int, Path(ge=1)],
    service: FormulationsServiceDep,
) -> FormulationResponse:
    return await service.get_formulation(formulation_id)


@router.patch("/{formulation_id}", response_model=FormulationResponse)
async def update_formulation(
    formulation_id: Annotated[int, Path(ge=1)],
    request: UpdateFormulationRequest,
    service: FormulationsServiceDep,
) -> FormulationResponse:
    return await service.update_formulation(formulation_id, request)


@router.delete("/{formulation_id}", response_model=FormulationResponse)
async def delete_formulation(
    formulation_id: Annotated[int, Path(ge=1)],
    service: FormulationsServiceDep,
) -> FormulationResponse:
    return await service.delete_formulation(formulation_id)
