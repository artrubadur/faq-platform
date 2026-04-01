from typing import Literal

from pydantic import BaseModel, Field, model_validator

QuestionFields = Literal["id", "question_text", "answer_text", "rating"]


class CreateQuestionRequest(BaseModel):
    question_text: str
    answer_text: str
    check_similarity: bool


class UpdateQuestionRequest(BaseModel):
    question_text: str | None = None
    answer_text: str | None = None
    rating: float | None = None
    recompute_embedding: bool = False


class ListQuestionsRequest(BaseModel):
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
    order_by: QuestionFields
    ascending: bool


class SuggestQuestionsRequest(BaseModel):
    question_text: str
    max_similar_amount: int = Field(ge=0)
    max_popular_amount: int = Field(ge=0)
    max_amount: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_limits(self) -> "SuggestQuestionsRequest":
        if self.max_similar_amount > self.max_amount:
            raise ValueError("'max_similar_amount' cannot be greater than 'max_amount'")
        if self.max_popular_amount > self.max_amount:
            raise ValueError("'max_popular_amount' cannot be greater than 'max_amount'")
        return self
