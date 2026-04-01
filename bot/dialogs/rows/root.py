from aiogram.types import InlineKeyboardButton

from bot.core.customization import messages


def go_row(dir: str):
    return [
        [
            InlineKeyboardButton(text=messages.misc.goto_go, callback_data=dir),
        ]
    ]
