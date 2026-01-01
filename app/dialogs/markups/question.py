from aiogram.types import InlineKeyboardMarkup

import app.dialogs.rows.base as rows
from app.core.constants.dirs import (
    QUESTIONS,
    QUESTIONS_CREATE,
    QUESTIONS_DELETE,
    QUESTIONS_UPDATE,
)

main = InlineKeyboardMarkup(
    inline_keyboard=rows.crud_rows(QUESTIONS[1]) + rows.back_row(QUESTIONS[0]),
)

back = InlineKeyboardMarkup(inline_keyboard=rows.back_row(QUESTIONS[1]))

cancel = InlineKeyboardMarkup(inline_keyboard=rows.cancel_row(QUESTIONS[1]))

confirm_creation = InlineKeyboardMarkup(
    inline_keyboard=rows.confirm_row(QUESTIONS_CREATE[1], QUESTIONS[1], "create")
)

confirm_similar = InlineKeyboardMarkup(
    inline_keyboard=rows.confirm_row(QUESTIONS_CREATE[1], QUESTIONS[1], "similar")
)

confirm_deletion = InlineKeyboardMarkup(
    inline_keyboard=rows.confirm_row(QUESTIONS_DELETE[1], QUESTIONS[1])
)

confirm_update = InlineKeyboardMarkup(
    inline_keyboard=rows.confirm_row(QUESTIONS_UPDATE[1], QUESTIONS[1], "update")
)

confirm_recompute = InlineKeyboardMarkup(
    inline_keyboard=rows.confirm_row(
        QUESTIONS_UPDATE[1], QUESTIONS_UPDATE[1], "recompute"
    )
)

field_save_update = InlineKeyboardMarkup(
    inline_keyboard=rows.field_rows(
        QUESTIONS_UPDATE[1],
        QUESTIONS[1],
        [
            rows.FieldButton("Question Text", "question_text"),
            rows.FieldButton("Answer Text", "answer_text"),
        ],
    )
)
