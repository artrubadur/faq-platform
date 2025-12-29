from aiogram.types import InlineKeyboardButton

from app.core.constants.emoji import EmojiMenu


def section_rows():
    return [
        [
            InlineKeyboardButton(
                text=f"{EmojiMenu.USERS} Users", callback_data="settings.users"
            ),
        ],
        [
            InlineKeyboardButton(
                text=f"{EmojiMenu.QUESTIONS} Questions",
                callback_data="settings.questions",
            ),
        ],
    ]
