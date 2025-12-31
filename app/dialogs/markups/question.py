from aiogram.types import InlineKeyboardMarkup

import app.dialogs.rows.base as rows

DIR = "settings.questions"


main = InlineKeyboardMarkup(
    inline_keyboard=rows.crud_rows(DIR) + rows.back_row("settings"),
)

back = InlineKeyboardMarkup(inline_keyboard=rows.back_row(DIR))

cancel = InlineKeyboardMarkup(inline_keyboard=rows.cancel_row(DIR))

confirm_creation = InlineKeyboardMarkup(
    inline_keyboard=rows.confirm_row(f"{DIR}.create", DIR, "create")
)

confirm_similar = InlineKeyboardMarkup(
    inline_keyboard=rows.confirm_row(f"{DIR}.create", DIR, "similar")
)

confirm_deletion = InlineKeyboardMarkup(
    inline_keyboard=rows.confirm_row(f"{DIR}.delete", DIR)
)

confirm_update = InlineKeyboardMarkup(
    inline_keyboard=rows.confirm_row(f"{DIR}.update", DIR, "update")
)

confirm_recompute = InlineKeyboardMarkup(
    inline_keyboard=rows.confirm_row(f"{DIR}.update", f"{DIR}.update", "recompute")
)

field_save_update = InlineKeyboardMarkup(
    inline_keyboard=rows.field_rows(
        f"{DIR}.update",
        DIR,
        [
            rows.FieldButton("Question Text", "question_text"),
            rows.FieldButton("Answer Text", "answer_text"),
        ],
    )
)
