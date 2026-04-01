from bot.services.http_client import orchestrator_client
from shared.contracts.question.requests import (
    CreateQuestionRequest,
    ListQuestionsRequest,
    QuestionFields,
    SuggestQuestionsRequest,
    UpdateQuestionRequest,
)
from shared.contracts.question.responses import (
    QuestionResponse,
    QuestionsAmountResponse,
    QuestionSuggestionResponse,
)
from shared.http.client import InternalApiClient


class QuestionGateway:
    def __init__(
        self,
        client: InternalApiClient,
    ) -> None:
        self.client = client

    async def get_question(self, id: int) -> QuestionResponse:
        data = await self.client.get(f"/questions/{id}")
        return QuestionResponse.model_validate(data)

    async def create_question(
        self,
        question_text: str,
        answer_text: str,
        check_similarity: bool,
    ) -> QuestionResponse:
        request = CreateQuestionRequest(
            question_text=question_text,
            answer_text=answer_text,
            check_similarity=check_similarity,
        )
        data = await self.client.post(
            "/questions",
            json_data=request.model_dump(mode="json"),
        )
        return QuestionResponse.model_validate(data)

    async def update_question(
        self,
        id: int,
        question_text: str | None = None,
        answer_text: str | None = None,
        rating: float | None = None,
        recompute_embedding: bool = False,
    ) -> QuestionResponse:
        request = UpdateQuestionRequest(
            question_text=question_text,
            answer_text=answer_text,
            rating=rating,
            recompute_embedding=recompute_embedding,
        )
        data = await self.client.patch(
            f"/questions/{id}",
            json_data=request.model_dump(mode="json"),
        )
        return QuestionResponse.model_validate(data)

    async def get_questions_amount(self) -> int:
        data = await self.client.get("/questions/count")
        return QuestionsAmountResponse.model_validate(data).amount

    async def get_paginated_questions(
        self,
        page: int,
        page_size: int,
        order_by: QuestionFields,
        ascending: bool,
    ) -> list[QuestionResponse]:
        request = ListQuestionsRequest(
            page=page,
            page_size=page_size,
            order_by=order_by,
            ascending=ascending,
        )
        data = await self.client.get(
            "/questions",
            params=request.model_dump(mode="json"),
        )
        return [QuestionResponse.model_validate(item) for item in data]

    async def delete_question(self, question_id: int) -> QuestionResponse:
        data = await self.client.delete(f"/questions/{question_id}")
        return QuestionResponse.model_validate(data)

    async def suggest_questions(
        self,
        question_text: str,
        max_similar_amount: int,
        max_popular_amount: int,
        max_amount: int,
    ) -> QuestionSuggestionResponse:
        request = SuggestQuestionsRequest(
            question_text=question_text,
            max_similar_amount=max_similar_amount,
            max_popular_amount=max_popular_amount,
            max_amount=max_amount,
        )
        data = await self.client.post(
            "/questions/suggest",
            json_data=request.model_dump(mode="json"),
        )
        return QuestionSuggestionResponse.model_validate(data)


question_gateway = QuestionGateway(orchestrator_client)
