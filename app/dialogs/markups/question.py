from aiogram.types import InlineKeyboardMarkup

import app.dialogs.rows.base as rows

main = InlineKeyboardMarkup(
    inline_keyboard=rows.crud_rows("settings.questions") + rows.back_row("settings"),
)

back = InlineKeyboardMarkup(inline_keyboard=rows.back_row("settings.questions"))

cancel = InlineKeyboardMarkup(inline_keyboard=rows.cancel_row("settings.questions"))

confirm_creation = InlineKeyboardMarkup(
    inline_keyboard=rows.confirm_row("settings.questions.create", "settings.questions", "create")
)

confirm_similar = InlineKeyboardMarkup(
    inline_keyboard=rows.confirm_row("settings.questions.create", "settings.questions", "similar")
)