from aiogram.types import InlineKeyboardMarkup

import app.dialogs.rows.base as brows

main = InlineKeyboardMarkup(
    inline_keyboard=brows.crud_rows("settings.users") + brows.back_row("settings"),
)

back = InlineKeyboardMarkup(inline_keyboard=brows.back_row("settings.users"))

cancel = InlineKeyboardMarkup(inline_keyboard=brows.cancel_row("settings.users"))

confirm_creation = InlineKeyboardMarkup(
    inline_keyboard=brows.confirm_row("settings.users.create", "settings.users")
)

confirm_deletion = InlineKeyboardMarkup(
    inline_keyboard=brows.confirm_row("settings.users.delete", "settings.users")
)

confirm_update = InlineKeyboardMarkup(
    inline_keyboard=brows.confirm_row("settings.users.update", "settings.users")
)

field_update = InlineKeyboardMarkup(
    inline_keyboard=brows.field_rows(
        "settings.users.update", "settings.users", ["username", "role"]
    )
)

# cancel_edit_field = InlineKeyboardMarkup(inline_keyboard=brows.cancel_row("settings.users.update"))
# confirm_save_update = InlineKeyboardMarkup(
#     inline_keyboard=rows.save_row("settings.users.update", "settings.users")
# )


# cancel_update_field = InlineKeyboardMarkup(inline_keyboard=cancel_markup("settings.users.update.process"))
