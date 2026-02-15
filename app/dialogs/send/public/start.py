from typing import Awaitable, Callable

from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from app.dialogs.actions import with_message_action
from app.storage.models import Question
from app.utils.format.output import format_response


@with_message_action
async def send_start(
    send: Callable[..., Awaitable[Message]],
    message: Message,
    text: str,
    questions: list[Question] = [],
) -> Message:
    if len(questions) == 0 or isinstance(questions, list) and len(questions) == 0:
        builder = ReplyKeyboardBuilder()
        for question in questions:
            builder.button(text=question.question_text)
        builder.adjust(1)
        reply_markup = builder.as_markup(resize_keyboard=True)
    else:
        reply_markup = ReplyKeyboardRemove()

    return await send(
        text=format_response(text, message),
        reply_markup=reply_markup,
    )
