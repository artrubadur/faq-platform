def validate_id(id: str | int) -> int:
    if isinstance(id, int):
        return id

    if id.isdigit():
        return int(id)

    raise ValueError("ID is incorrect")


def validate_question_text(question_text: str) -> str:
    lenght = len(question_text)
    if lenght > 384:
        raise ValueError(f"The question text is too long ({lenght})")
    return question_text


def validate_answer_text(question_text: str) -> str:
    lenght = len(question_text)
    if lenght > 384:
        raise ValueError(f"The answer text is too long ({lenght})")
    return question_text
