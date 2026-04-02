from typing import Annotated

from fastapi import APIRouter, Depends, Query

from orchestrator.api.dependencies import QuestionsServiceDep
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

router = APIRouter(prefix="/questions", tags=["questions"])


@router.post("", response_model=QuestionResponse)
async def create_question(
    request: CreateQuestionRequest,
    service: QuestionsServiceDep,
) -> QuestionResponse:
    return await service.create_question(request)


@router.post("/suggest", response_model=QuestionSuggestionResponse)
async def suggest_questions(
    request: SuggestQuestionsRequest,
    service: QuestionsServiceDep,
) -> QuestionSuggestionResponse:
    return await service.suggest_questions(request)


@router.get("/count", response_model=QuestionsAmountResponse)
async def get_questions_amount(service: QuestionsServiceDep) -> QuestionsAmountResponse:
    return await service.get_questions_amount()


@router.get("", response_model=list[QuestionResponse])
async def get_paginated_questions(
    request: Annotated[ListQuestionsRequest, Depends()],
    service: QuestionsServiceDep,
) -> list[QuestionResponse]:
    return await service.get_paginated_questions(request)


@router.get("/popular", response_model=list[QuestionResponse])
async def get_popular_questions(
    amount: Annotated[int, Query(ge=0)],
    service: QuestionsServiceDep,
) -> list[QuestionResponse]:
    return await service.get_popular_questions(amount)


@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(
    question_id: int,
    service: QuestionsServiceDep,
) -> QuestionResponse:
    return await service.get_question(question_id)


@router.patch("/{question_id}", response_model=QuestionResponse)
async def update_question(
    question_id: int,
    request: UpdateQuestionRequest,
    service: QuestionsServiceDep,
) -> QuestionResponse:
    return await service.update_question(question_id, request)


@router.delete("/{question_id}", response_model=QuestionResponse)
async def delete_question(
    question_id: int,
    service: QuestionsServiceDep,
) -> QuestionResponse:
    return await service.delete_question(question_id)
