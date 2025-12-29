from aiogram.types import InlineKeyboardButton


def go_row(dir: str):
    return [
        [
            InlineKeyboardButton(text="Go!", callback_data=dir),
        ]
    ]
