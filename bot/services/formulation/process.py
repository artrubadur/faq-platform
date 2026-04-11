from aiogram.types import Message

from bot.core.customization import messages
from bot.services.formulation.validate import (
    validate_id,
    validate_question_id,
    validate_question_text,
)
from bot.utils.format.input import format_input


def process_id_msg(message: Message) -> int:
    input_id = message.text
    if input_id is None:
        raise ValueError(messages.process.formulation.id_invalid)

    formatted_id = format_input(input_id)
    valid_id = validate_id(formatted_id)
    return valid_id


def process_question_id_msg(message: Message) -> int:
    input_question_id = message.text
    if input_question_id is None:
        raise ValueError(messages.process.formulation.question_id_invalid)

    formatted_question_id = format_input(input_question_id)
    valid_question_id = validate_question_id(formatted_question_id)
    return valid_question_id


def process_question_text_msg(message: Message) -> str:
    input_question_text = message.text
    if input_question_text is None:
        raise ValueError(messages.process.formulation.question_text_invalid)

    formatted_question_text = format_input(input_question_text)
    valid_question_text = validate_question_text(formatted_question_text)
    return valid_question_text
