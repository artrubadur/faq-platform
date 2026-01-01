from aiogram.types import InlineKeyboardMarkup

import app.dialogs.rows.base as rows
from app.core.constants.dirs import (
    SETTINGS,
    USERS_CREATE,
    USERS_DELETE,
    USERS_LIST,
    USERS_UPDATE,
)
from app.repositories.users import UserColumn

main = InlineKeyboardMarkup(
    inline_keyboard=rows.crud_rows(USERS_DELETE[0]) + rows.back_row(SETTINGS),
)

back = InlineKeyboardMarkup(inline_keyboard=rows.back_row(USERS_DELETE[0]))

cancel = InlineKeyboardMarkup(inline_keyboard=rows.cancel_row(USERS_DELETE[0]))

confirm_creation = InlineKeyboardMarkup(
    inline_keyboard=rows.confirm_row(USERS_CREATE[1], USERS_DELETE[0])
)

confirm_deletion = InlineKeyboardMarkup(
    inline_keyboard=rows.confirm_row(USERS_DELETE[1], USERS_DELETE[0])
)

confirm_update = InlineKeyboardMarkup(
    inline_keyboard=rows.confirm_row(USERS_UPDATE[1], USERS_DELETE[0])
)

field_save_update = InlineKeyboardMarkup(
    inline_keyboard=rows.field_rows(
        USERS_UPDATE[1],
        USERS_DELETE[0],
        [rows.FieldButton("Username", "username"), rows.FieldButton("Role", "role")],
    )
)


def make_listing_markup(
    order: str,
    ascending: bool,
    page_size: int,
    has_prev: bool,
    has_next: bool,
):
    return InlineKeyboardMarkup(
        inline_keyboard=rows.pagin_order_row(USERS_LIST[1], UserColumn, order)
        + rows.pagin_direction_row(USERS_LIST[1], ascending)
        + rows.pagin_size_row(USERS_LIST[1], [5, 10, 25, 50], page_size)
        + rows.pagin_page_row(USERS_LIST[1], has_prev, has_next)
    )
