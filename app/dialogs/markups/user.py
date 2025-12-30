from aiogram.types import InlineKeyboardMarkup

import app.dialogs.rows.base as rows

main = InlineKeyboardMarkup(
    inline_keyboard=rows.crud_rows("settings.users") + rows.back_row("settings"),
)

back = InlineKeyboardMarkup(inline_keyboard=rows.back_row("settings.users"))

cancel = InlineKeyboardMarkup(inline_keyboard=rows.cancel_row("settings.users"))

confirm_creation = InlineKeyboardMarkup(
    inline_keyboard=rows.confirm_row("settings.users.create", "settings.users")
)

confirm_deletion = InlineKeyboardMarkup(
    inline_keyboard=rows.confirm_row("settings.users.delete", "settings.users")
)

confirm_update = InlineKeyboardMarkup(
    inline_keyboard=rows.confirm_row("settings.users.update", "settings.users")
)

field_save_update = InlineKeyboardMarkup(
    inline_keyboard=rows.field_rows(
        "settings.users.update", "settings.users", ["username", "role"]
    )
)
