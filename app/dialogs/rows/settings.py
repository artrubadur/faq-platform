from aiogram.types import InlineKeyboardButton

from app.core.constants.dirs import QUESTIONS, USERS
from app.core.messages import messages


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
