from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton

import bot.dialogs.rows.common as rows
from bot.core.customization import messages
from bot.core.dirs import FORMULATIONS

cancel_row = rows.cancel_row(FORMULATIONS[1])


class IdCallback(CallbackData, prefix="fid"):
    dir: str
    id: int


def id_row(
    dir: str,
    found_formulation_id: int | None = None,
):
    result = []
    if found_formulation_id is not None:
        callback_data = IdCallback(dir=dir, id=found_formulation_id).pack()
        result.append(
            [
                InlineKeyboardButton(
                    text=messages.button.formulation.found.format(
                        id=found_formulation_id
                    ),
                    callback_data=callback_data,
                )
            ]
        )

    return result


class ScopeCallback(CallbackData, prefix="fsc"):
    dir: str
    cancel: bool


def scope_row(
    dir: str,
    question_id_scope: int | None,
):
    if question_id_scope is None:
        return [
            [
                InlineKeyboardButton(
                    text=messages.button.formulation.filter_by_question,
                    callback_data=ScopeCallback(dir=dir, cancel=False).pack(),
                )
            ]
        ]

    return [
        [
            InlineKeyboardButton(
                text=messages.button.formulation.cancel_scope,
                callback_data=ScopeCallback(dir=dir, cancel=True).pack(),
            )
        ]
    ]
