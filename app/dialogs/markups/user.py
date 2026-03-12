from aiogram.types import InlineKeyboardMarkup

import app.dialogs.rows.common as rows
from app.core.customization import messages
from app.core.dirs import USERS, USERS_CREATE, USERS_DELETE, USERS_LIST, USERS_UPDATE

main = InlineKeyboardMarkup(
    inline_keyboard=rows.crud_rows(USERS[1])
    + rows.list_row(USERS[1])
    + rows.back_row(USERS[0]),
)

back = InlineKeyboardMarkup(inline_keyboard=rows.back_row(USERS[1]))

cancel = InlineKeyboardMarkup(inline_keyboard=rows.cancel_row(USERS[1]))

confirm_creation = InlineKeyboardMarkup(
    inline_keyboard=rows.confirm_row(USERS_CREATE[1], USERS[1])
)

confirm_deletion = InlineKeyboardMarkup(
    inline_keyboard=rows.confirm_row(USERS_DELETE[1], USERS[1])
)

confirm_update = InlineKeyboardMarkup(
    inline_keyboard=rows.confirm_row(USERS_UPDATE[1], USERS[1])
)

field_save_update = InlineKeyboardMarkup(
    inline_keyboard=rows.field_rows(
        USERS_UPDATE[1],
        USERS[1],
        [
            rows.FieldButton(messages.button.user.username, "username"),
            rows.FieldButton(messages.button.user.role, "role"),
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
        inline_keyboard=rows.pagin_order_row(USERS_LIST[1], columns, order, ascending)
        + rows.pagin_size_row(USERS_LIST[1], [5, 10, 25, 50], page_size)
        + rows.pagin_page_row(USERS_LIST[1], has_prev, has_next)
        + rows.back_row(USERS_LIST[0])
    )
