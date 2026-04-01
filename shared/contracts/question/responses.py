from pydantic import BaseModel, ConfigDict


class QuestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    question_text: str
    answer_text: str
    rating: float = 0.0


class QuestionSuggestionResponse(BaseModel):
    questions: list[QuestionResponse]
    is_confident: bool


class QuestionsAmountResponse(BaseModel):
    amount: int
