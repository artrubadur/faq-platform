from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class QuestionDto:
    id: int
    question_text: str
    answer_text: str


@dataclass(slots=True, frozen=True)
class QuestionSuggestionDto:
    questions: list[QuestionDto]
    is_confident: bool
