from typing import Awaitable, Callable

from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bot.core.customization import messages
from bot.dialogs.actions import with_message_action
from bot.utils.format.output import format_response
from shared.contracts.question.responses import QuestionResponse


@with_message_action
async def send_start(
    send: Callable[..., Awaitable[Message]],
    message: Message,
    questions: list[QuestionResponse] = [],
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
        text=format_response(messages.responses.public.start, message),
        parse_mode=messages.parse_mode,
        reply_markup=reply_markup,
    )
