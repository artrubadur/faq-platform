from typing import Awaitable, Callable

from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from app.dialogs.actions import with_message_action
from app.storage.models.question import Question


@with_message_action
async def send_similar(
    send: Callable[..., Awaitable[Message]], questions: list[Question]
) -> Message:
    builder = ReplyKeyboardBuilder()
    for question in questions[1:]:
        builder.button(text=question.question_text)
    builder.adjust(1)
    reply_markup = builder.as_markup(resize_keyboard=True)

    most_similar = questions[0]
    return await send(
        text=most_similar.answer_text, reply_markup=reply_markup, parse_mode="HTML"
    )


@with_message_action
async def send_failed(
    send: Callable[..., Awaitable[Message]],
    exception: str,
    fallback_questions: list[Question] = [],
) -> Message:
    builder = ReplyKeyboardBuilder()
    for question in fallback_questions[1:]:
        builder.button(text=question.question_text)
    builder.adjust(1)
    reply_markup = builder.as_markup(resize_keyboard=True)

    return await send(
        text=f"{exception}. Try to reformulate it and ask again",
        reply_markup=reply_markup,
    )
