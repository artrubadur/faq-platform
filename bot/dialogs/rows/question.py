from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton

import bot.dialogs.rows.common as rows
from bot.core.customization import messages
from bot.core.dirs import QUESTIONS

cancel_row = rows.cancel_row(QUESTIONS[1])


class IdCallback(CallbackData, prefix="id"):
    dir: str
    id: int


def id_row(
    dir: str,
    found_question_id: int | None = None,
):
    rows = []
    if found_question_id is not None:
        callback_data = IdCallback(dir=dir, id=found_question_id).pack()
        rows.append(
            [
                InlineKeyboardButton(
                    text=messages.button.question.found.format(id=found_question_id),
                    callback_data=callback_data,
                )
            ]
        )

    return rows
