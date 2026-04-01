from pydantic import BaseModel


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
    page: int
    page_size: int
    order_by: str
    ascending: bool


class SuggestQuestionsRequest(BaseModel):
    question_text: str
    max_similar_amount: int
    max_popular_amount: int
    max_amount: int
