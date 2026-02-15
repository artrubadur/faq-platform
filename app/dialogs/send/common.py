from typing import Any, Awaitable, Callable

from aiogram.types import InlineKeyboardMarkup, Message

import app.dialogs.rows.common as rows
from app.core.constants.emojis import EmojiAction, EmojiStatus
from app.dialogs.actions import with_chat_message, with_message_action


@with_message_action
async def send_invalid(
    send: Callable[..., Awaitable[Message]], cancel_dir: str, text: str | None
) -> Message:
    reply_markup = InlineKeyboardMarkup(inline_keyboard=rows.back_row(cancel_dir))

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
async def send_log(
    send: Callable[..., Awaitable[Message]],
    name: str,
    message: str,
    level: Any,
    exception: Exception | None,
    repeat: int | None,
    repeat_limit: int,
) -> Message:

    repeat_str = f"Repeat: {repeat}/{repeat_limit}\n" if repeat is not None else ""
    error_str = (
        f"Error: `{exception.type} {exception.value}`\n"
        if exception is not None
        else ""
    )
    return await send(
        text=(
            f"{level.icon} [{level.name}] from `{name}`\n"
            f"{repeat_str}"
            f"Log: `{message}`\n"
            f"{error_str}"
            f"{EmojiAction.GET} Check the logs for more"
        ),
        parse_mode="Markdown",
    )
