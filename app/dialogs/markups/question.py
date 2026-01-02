from aiogram.types import InlineKeyboardMarkup

import app.dialogs.rows.common as rows
from app.core.constants.dirs import (
    QUESTIONS,
    QUESTIONS_CREATE,
    QUESTIONS_DELETE,
    QUESTIONS_UPDATE,
    QUESTIONS_LIST,
)

main = InlineKeyboardMarkup(
    inline_keyboard=rows.crud_rows(QUESTIONS[1]) + rows.list_row(QUESTIONS[1]) + rows.back_row(QUESTIONS[0]),
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

def make_listing_markup(
    columns: list[str],
    order: str,
    ascending: bool,
    page_size: int,
    has_prev: bool,
    has_next: bool,
):
    return InlineKeyboardMarkup(
        inline_keyboard=rows.pagin_order_row(QUESTIONS_LIST[1], columns, order, ascending)
        + rows.pagin_size_row(QUESTIONS_LIST[1], [3, 5, 10, 25], page_size)
        + rows.pagin_page_row(QUESTIONS_LIST[1], has_prev, has_next)
        + rows.back_row(QUESTIONS_LIST[0])
    )
