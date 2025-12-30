# pyright: reportArgumentType=false
from aiogram.types import Message

from app.services.question.validate import validate_question_text
from app.utils.format.input import format_input


async def process_question_text_msg(message: Message):
    input_question_text = message.html_text
    if input_question_text is None:
        raise ValueError("Invalid message type")

    input_question_text = format_input(input_question_text)
    valid_question_text = validate_question_text(input_question_text)
    return valid_question_text


async def process_answer_text_msg(message: Message):
    input_answer_text = message.html_text
    if input_answer_text is None:
        raise ValueError("Invalid message type")

    input_answer_text = format_input(input_answer_text)
    valid_answer_text = validate_question_text(input_answer_text)
    return valid_answer_text
