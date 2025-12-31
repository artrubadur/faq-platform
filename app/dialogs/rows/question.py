from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton

import app.dialogs.rows.base as rows

DIR = "settings.questions"

cancel_row = rows.cancel_row(DIR)


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
                    text=f"Found ({found_question_id})",
                    callback_data=callback_data,
                )
            ]
        )

    return rows
