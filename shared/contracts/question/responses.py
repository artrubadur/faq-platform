from pydantic import BaseModel, ConfigDict, Field

from shared.contracts.types import Int64Id


class QuestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Int64Id
    question_text: str
    answer_text: str
    rating: float = 0.0


class QuestionFormulationsResponse(QuestionResponse):
    formulation_ids: list[Int64Id] = Field(default_factory=list)


class QuestionSuggestionResponse(BaseModel):
    questions: list[QuestionResponse]
    is_confident: bool


class QuestionsAmountResponse(BaseModel):
    amount: int
