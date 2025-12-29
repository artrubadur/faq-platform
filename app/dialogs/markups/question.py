from aiogram.types import InlineKeyboardMarkup

import app.dialogs.rows.base as brows

main = InlineKeyboardMarkup(
    inline_keyboard=brows.crud_rows("settings.questions") + brows.back_row("settings"),
)
