from aiogram.types import InlineKeyboardButton

from app.core.customization import messages
from app.core.dirs import QUESTIONS, USERS


def section_rows():
    return [
        [
            InlineKeyboardButton(
                text=messages.button.settings.user, callback_data=USERS[1]
            ),
        ],
        [
            InlineKeyboardButton(
                text=messages.button.settings.question,
                callback_data=QUESTIONS[1],
            ),
        ],
    ]
