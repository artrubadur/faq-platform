from typing import Awaitable, Callable

from aiogram.types import InlineKeyboardMarkup, Message

import app.dialogs.rows.common as rows
from app.core.constants.emojis import EmojiStatus
from app.dialogs.actions import action_wrapper


@action_wrapper
async def send_invalid(
    send: Callable[..., Awaitable[Message]], dir: str, text: str | None
) -> Message:
    reply_markup = InlineKeyboardMarkup(inline_keyboard=rows.back_row(dir))

    return await send(
        text=f"{EmojiStatus.WARNING} {text}. Retry or back",
        reply_markup=reply_markup,
    )
