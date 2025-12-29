from typing import Optional

from aiogram.types import InlineKeyboardMarkup, Message

import app.dialogs.rows.root as rows
from app.core.constants.emoji import EmojiAction
from app.utils.format.output import format_invalid_output


async def send_confirm_goto(message: Message, to_dir: str):
    reply_markup = InlineKeyboardMarkup(inline_keyboard=rows.go_row(to_dir))

    await message.answer(
        f"{EmojiAction.SELECT} Go to `{to_dir}`?",
        parse_mode="Markdown",
        reply_markup=reply_markup,
    )


async def send_invalid_path(
    message: Message, item: Optional[str] = None, exception: Optional[str] = None
):
    await message.answer(format_invalid_output(item, exception))
