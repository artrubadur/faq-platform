from pydantic import BaseModel


class QuestionResponse(BaseModel):
    id: int
    question_text: str
    answer_text: str
    rating: float = 0.0


class QuestionSuggestionResponse(BaseModel):
    questions: list[QuestionResponse]
    is_confident: bool


class QuestionsAmountResponse(BaseModel):
    amount: int
