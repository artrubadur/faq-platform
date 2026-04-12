from bot.core.config import config
from bot.core.customization import messages
from bot.services.common.validate import validate_int64_id


def validate_id(id: str | int) -> int:
    return validate_int64_id(id, messages.validation.question.id_invalid)


def validate_question_text(question_text: str) -> str:
    lenght = len(question_text)
    if lenght > config.question_limits.max_question_text_len:
        raise ValueError(messages.validation.question.question_text_long)
    return question_text


def validate_answer_text(question_text: str) -> str:
    lenght = len(question_text)
    if lenght > config.question_limits.max_answer_text_len:
        raise ValueError(messages.validation.question.answer_text_long)
    return question_text


def validate_rating(rating: str) -> float:
    try:
        return float(rating)
    except ValueError as exc:
        raise ValueError(messages.validation.question.rating_incorrect) from exc
