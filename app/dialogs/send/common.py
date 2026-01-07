from typing import Awaitable, Callable

from aiogram.types import InlineKeyboardMarkup, Message

import app.dialogs.rows.common as rows
from app.core.constants.emojis import EmojiStatus
from app.dialogs.actions import action_wrapper, with_chat_message


@action_wrapper
async def send_invalid(
    send: Callable[..., Awaitable[Message]], dir: str, text: str | None
) -> Message:
    reply_markup = InlineKeyboardMarkup(inline_keyboard=rows.back_row(dir))

    return await send(
        text=f"{EmojiStatus.WARNING} {text}. Retry or back",
        reply_markup=reply_markup,
    )


@action_wrapper
async def send_unexcepted_error(send: Callable[..., Awaitable[Message]]) -> Message:
    return await send(
        text=f"{EmojiStatus.FAILED} Unexcepted error! We are already fixing it. Try to retry later"
    )


@with_chat_message
async def send_unhandled_exception(
    send: Callable[..., Awaitable[Message]], exception: Exception
) -> Message:
    return await send(
        text=f"{EmojiStatus.FAILED} Unhandled error: `{exception}`. Check the logs",
        parse_mode="Markdown",
    )
