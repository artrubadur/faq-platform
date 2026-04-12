from bot.core.config import config
from bot.core.customization import messages
from bot.services.common.validate import validate_int64_id


def _validate_positive_int(value: str | int, error_message: str) -> int:
    return validate_int64_id(value, error_message)


def validate_id(id: str | int) -> int:
    return _validate_positive_int(id, messages.validation.formulation.id_invalid)


def validate_question_id(question_id: str | int) -> int:
    return _validate_positive_int(
        question_id,
        messages.validation.formulation.question_id_invalid,
    )


def validate_question_text(question_text: str) -> str:
    length = len(question_text)
    if length > config.question_limits.max_question_text_len:
        raise ValueError(messages.validation.formulation.question_text_long)
    return question_text
