from bot.services.api.client import InternalApiClient, client
from bot.services.api.schemas.question import QuestionDto, QuestionSuggestionDto


class QuestionGateway:
    def __init__(
        self,
        client: InternalApiClient,
    ) -> None:
        self.client = client

    async def get_question(self, question_id: int) -> QuestionDto:
        data = await self.client.get(f"/questions/{question_id}")
        return QuestionDto(**data)

    async def create_question(
        self,
        question_text: str,
        answer_text: str,
        check_similarity: bool,
    ) -> QuestionDto:
        data = await self.client.post(
            "/questions",
            json_data={
                "question_text": question_text,
                "answer_text": answer_text,
                "check_similarity": check_similarity,
            },
        )
        return QuestionDto(**data)

    async def update_question(
        self,
        question_id: int,
        question_text: str | None,
        answer_text: str | None,
        rating: float | None,
        recompute_embedding: bool,
    ) -> QuestionDto:
        data = await self.client.patch(
            f"/questions/{question_id}",
            json_data={
                "question_text": question_text,
                "answer_text": answer_text,
                "rating": rating,
                "recompute_embedding": recompute_embedding,
            },
        )
        return QuestionDto(**data)

    async def get_questions_amount(self) -> int:
        data = await self.client.get("/questions/count")
        return int(data["amount"])

    async def get_paginated_questions(
        self,
        page: int,
        page_size: int,
        order_by: str,
        ascending: bool,
    ) -> list[QuestionDto]:
        data = await self.client.get(
            "/questions",
            params={
                "page": page,
                "page_size": page_size,
                "order_by": order_by,
                "ascending": ascending,
            },
        )
        return [QuestionDto.model_validate(item) for item in data]

    async def delete_question(self, question_id: int) -> QuestionDto:
        data = await self.client.delete(f"/questions/{question_id}")
        return QuestionDto(**data)

    async def suggest_questions(
        self,
        question_text: str,
        max_similar_amount: int,
        max_popular_amount: int,
        max_amount: int,
    ) -> QuestionSuggestionDto:
        data = await self.client.post(
            "/questions/suggest",
            json_data={
                "question_text": question_text,
                "max_similar_amount": max_similar_amount,
                "max_popular_amount": max_popular_amount,
                "max_amount": max_amount,
            },
        )
        return QuestionSuggestionDto(**data)


question_gateway = QuestionGateway(client)
