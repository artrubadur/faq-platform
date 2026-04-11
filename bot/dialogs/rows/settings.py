from aiogram.types import InlineKeyboardButton

from bot.core.customization import messages
from bot.core.dirs import FORMULATIONS, QUESTIONS, USERS


def section_rows():
    return [
        [
            InlineKeyboardButton(
                text=messages.button.settings.user, callback_data=USERS[1]
            ),
            InlineKeyboardButton(
                text=messages.button.settings.question,
                callback_data=QUESTIONS[1],
            ),
            InlineKeyboardButton(
                text=messages.button.settings.formulation,
                callback_data=FORMULATIONS[1],
            ),
        ],
    ]
