from aiogram.filters import CommandObject
from aiogram.types import Message

from app.services.question.validate import (
    validate_id,
    validate_question_text,
    validate_rating,
)
from app.utils.format.input import format_input


async def process_id_msg(message: Message):
    input_id = message.text
    if input_id is None:
        raise ValueError("Please send a simple text message with ID")

    formatted_id = format_input(input_id)
    valid_id = validate_id(formatted_id)
    return valid_id


async def process_question_text_msg(message: Message):
    input_question_text = message.text
    if input_question_text is None:
        raise ValueError("Please send a simple text message with the question")

    formatted_question_text = format_input(input_question_text)
    valid_question_text = validate_question_text(formatted_question_text)
    return valid_question_text


async def process_question_text_cmd(command: CommandObject):
    input_question_text = command.args
    if input_question_text is None:
        raise ValueError("Please specify the question text after the command")

    formatted_question_text = format_input(input_question_text)
    valid_question_text = validate_question_text(formatted_question_text)
    return valid_question_text


async def process_answer_text_msg(message: Message):
    input_answer_text = message.html_text
    if input_answer_text is None:
        raise ValueError(
            "Please send a simple text message with the answer to the question"
        )

    formatted_answer_text = format_input(input_answer_text)
    valid_answer_text = validate_question_text(formatted_answer_text)
    return valid_answer_text


async def process_rating_msg(message: Message):
    input_rating = message.text
    if input_rating is None:
        raise ValueError("Please send a simple text message with the rating")

    formatted_rating = format_input(input_rating)
    valid_rating = validate_rating(formatted_rating)
    return valid_rating
