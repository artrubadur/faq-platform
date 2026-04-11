from aiogram.types import InlineKeyboardMarkup

import bot.dialogs.rows.common as rows
import bot.dialogs.rows.formulation as frows
from bot.core.customization import messages
from bot.core.dirs import (
    FORMULATIONS,
    FORMULATIONS_CREATE,
    FORMULATIONS_DELETE,
    FORMULATIONS_LIST,
    FORMULATIONS_UPDATE,
)

main = InlineKeyboardMarkup(
    inline_keyboard=rows.crud_rows(FORMULATIONS[1])
    + rows.list_row(FORMULATIONS[1])
    + rows.back_row(FORMULATIONS[0]),
)

back = InlineKeyboardMarkup(inline_keyboard=rows.back_row(FORMULATIONS[1]))

cancel = InlineKeyboardMarkup(inline_keyboard=rows.cancel_row(FORMULATIONS[1]))

confirm_creation = InlineKeyboardMarkup(
    inline_keyboard=rows.confirm_row(FORMULATIONS_CREATE[1], FORMULATIONS[1])
)

confirm_deletion = InlineKeyboardMarkup(
    inline_keyboard=rows.confirm_row(FORMULATIONS_DELETE[1], FORMULATIONS[1])
)

confirm_update = InlineKeyboardMarkup(
    inline_keyboard=rows.confirm_row(FORMULATIONS_UPDATE[1], FORMULATIONS[1], "update")
)

confirm_recompute = InlineKeyboardMarkup(
    inline_keyboard=rows.confirm_row(
        FORMULATIONS_UPDATE[1], FORMULATIONS_UPDATE[1], "recompute"
    )
)

field_save_update = InlineKeyboardMarkup(
    inline_keyboard=rows.field_rows(
        FORMULATIONS_UPDATE[1],
        FORMULATIONS[1],
        [
            rows.FieldButton(
                messages.button.formulation.question_text, "question_text"
            ),
            rows.FieldButton(messages.button.formulation.question_id, "question_id"),
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
    question_id_scope: int | None,
):
    return InlineKeyboardMarkup(
        inline_keyboard=rows.pagin_order_row(
            FORMULATIONS_LIST[1], columns, order, ascending
        )
        + rows.pagin_size_row(FORMULATIONS_LIST[1], [3, 5, 10, 25], page_size)
        + rows.pagin_page_row(FORMULATIONS_LIST[1], has_prev, has_next)
        + frows.scope_row(FORMULATIONS_LIST[1], question_id_scope)
        + rows.back_row(FORMULATIONS_LIST[0])
    )
