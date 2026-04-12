from aiogram.filters import CommandObject
from aiogram.types import Message

from bot.core.customization import messages
from bot.services.question.validate import (
    validate_generate_formulations_amount,
    validate_id,
    validate_question_text,
    validate_rating,
)
from bot.utils.format.input import format_input


def process_id_msg(message: Message):
    input_id = message.text
    if input_id is None:
        raise ValueError(messages.process.question.id_invalid)

    formatted_id = format_input(input_id)
    valid_id = validate_id(formatted_id)
    return valid_id


def process_question_text_msg(message: Message):
    input_question_text = message.text
    if input_question_text is None:
        raise ValueError(messages.process.question.msg_question_text_invalid)

    formatted_question_text = format_input(input_question_text)
    valid_question_text = validate_question_text(formatted_question_text)
    return valid_question_text


def process_question_text_cmd(command: CommandObject):
    input_question_text = command.args
    if input_question_text is None:
        raise ValueError(messages.process.question.cmd_question_text_invalid)

    formatted_question_text = format_input(input_question_text)
    valid_question_text = validate_question_text(formatted_question_text)
    return valid_question_text


def process_answer_text_msg(message: Message):
    input_answer_text = message.html_text
    if input_answer_text is None:
        raise ValueError(messages.process.question.answer_text_invalid)

    formatted_answer_text = format_input(input_answer_text)
    valid_answer_text = validate_question_text(formatted_answer_text)
    return valid_answer_text


def process_rating_msg(message: Message):
    input_rating = message.text
    if input_rating is None:
        raise ValueError(messages.process.question.rating_invalid)

    formatted_rating = format_input(input_rating)
    valid_rating = validate_rating(formatted_rating)
    return valid_rating


def process_generation_amount_msg(message: Message):
    input_amount = message.text
    if input_amount is None:
        raise ValueError(messages.process.question.generation_amount_invalid)

    formatted_amount = format_input(input_amount)
    valid_amount = validate_generate_formulations_amount(formatted_amount)
    return valid_amount
