from typing import Awaitable, Callable

from aiogram.types import InlineKeyboardMarkup, Message

import app.dialogs.rows.common as rows
from app.core.constants.emojis import EmojiStatus
from app.dialogs.actions import with_chat_message, with_message_action


@with_message_action
async def send_invalid(
    send: Callable[..., Awaitable[Message]], dir: str, text: str | None
) -> Message:
    reply_markup = InlineKeyboardMarkup(inline_keyboard=rows.back_row(dir))

    return await send(
        text=f"{EmojiStatus.WARNING} {text}. Retry or back",
        reply_markup=reply_markup,
    )


@with_message_action
async def send_unexcepted_error(send: Callable[..., Awaitable[Message]]) -> Message:
    return await send(
        text=f"{EmojiStatus.FAILED} Unexcepted internal error! We are already fixing it. Try to retry"
    )


@with_chat_message
async def send_unhandled_exception(
    send: Callable[..., Awaitable[Message]], exception: Exception
) -> Message:
    return await send(
        text=f"{EmojiStatus.FAILED} Unhandled error: `{exception}`\nCheck the logs",
        parse_mode="Markdown",
    )
