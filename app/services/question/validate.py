from app.core.messages import messages


def validate_id(id: str | int) -> int:
    if isinstance(id, int):
        return id

    if id.isdigit():
        return int(id)

    raise ValueError(messages.validation.question.id_invalid)


def validate_question_text(question_text: str) -> str:
    lenght = len(question_text)
    if lenght > 384:
        raise ValueError(messages.validation.question.question_text_long)
    return question_text


def validate_answer_text(question_text: str) -> str:
    lenght = len(question_text)
    if lenght > 384:
        raise ValueError(messages.validation.question.answer_text_long)
    return question_text


def validate_rating(rating: str) -> float:
    try:
        return float(rating)
    except ValueError:
        raise ValueError(messages.validation.question.rating_incorrect)
