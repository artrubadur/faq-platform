from aiogram.types import InlineKeyboardButton

from app.core.customization import messages


def go_row(dir: str):
    return [
        [
            InlineKeyboardButton(text=messages.misc.goto_go, callback_data=dir),
        ]
    ]
