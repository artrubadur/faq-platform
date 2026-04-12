from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

QuestionFields = Literal["id", "question_text", "answer_text", "rating"]


class CreateQuestionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question_text: str
    answer_text: str
    check_similarity: bool
    generate_formulations_amount: int = Field(default=0, ge=0)


class UpdateQuestionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question_text: str | None = None
    answer_text: str | None = None
    rating: float | None = None
    generate_formulations_amount: int | None = Field(default=None, ge=0)


class ListQuestionsRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
    order_by: QuestionFields
    ascending: bool


class SuggestQuestionsRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

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
