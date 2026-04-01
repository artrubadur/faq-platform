from typing import Awaitable, Callable

from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bot.core.customization import messages
from bot.dialogs.actions import with_message_action
from bot.utils.format.output import format_response
from shared.contracts.question.responses import QuestionResponse


@with_message_action
async def send_similar(
    send: Callable[..., Awaitable[Message]],
    message: Message,
    suggestions: list[QuestionResponse],
) -> Message:
    builder = ReplyKeyboardBuilder()
    for question in suggestions[1:]:
        builder.button(text=question.question_text)
    builder.adjust(1)
    reply_markup = builder.as_markup(resize_keyboard=True)

    most_similar = suggestions[0]
    return await send(
        text=most_similar.answer_text,
        reply_markup=reply_markup,
        parse_mode=messages.parse_mode,
    )


@with_message_action
async def send_failed(
    send: Callable[..., Awaitable[Message]],
    message: Message,
    exception: str,
    suggestions: list[QuestionResponse] = [],
) -> Message:
    builder = ReplyKeyboardBuilder()
    for question in suggestions[1:]:
        builder.button(text=question.question_text)
    builder.adjust(1)
    reply_markup = builder.as_markup(resize_keyboard=True)

    return await send(
        text=format_response(
            messages.responses.public.failed, message, exception=exception
        ),
        parse_mode=messages.parse_mode,
        reply_markup=reply_markup,
    )
