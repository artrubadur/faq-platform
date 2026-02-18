from dataclasses import dataclass

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton

from app.core.constants.dirs import CREATE, DELETE, GET, LIST, UPDATE
from app.core.messages import messages


class CloseCallback(CallbackData, prefix="cls"):
    pass


def close_row():
    return [
        [
            InlineKeyboardButton(
                text=messages.button.common.close,
                callback_data=CloseCallback().pack(),
            )
        ]
    ]


class BackCallback(CallbackData, prefix="bck"):
    dir: str


def back_row(dir: str):
    return [
        [
            InlineKeyboardButton(
                text=messages.button.common.back,
                callback_data=BackCallback(dir=dir).pack(),
            ),
        ]
    ]


class CancelCallback(CallbackData, prefix="cnc"):
    dir: str


def cancel_row(dir: str):
    return [
        [
            InlineKeyboardButton(
                text=messages.button.common.cancel,
                callback_data=CancelCallback(dir=dir).pack(),
            ),
        ]
    ]


class ConfirmCallback(CallbackData, prefix="cfm"):
    dir: str
    step: str


def confirm_row(confirm_dir: str, cancel_dir: str, step: str = ""):
    return [
        [
            InlineKeyboardButton(
                text=messages.button.common.confirm,
                callback_data=ConfirmCallback(dir=confirm_dir, step=step).pack(),
            ),
            InlineKeyboardButton(
                text=messages.button.common.reject,
                callback_data=CancelCallback(dir=cancel_dir).pack(),
            ),
        ]
    ]


class SaveCallback(CallbackData, prefix="sav"):
    dir: str


def save_row(save_dir: str, cancel_dir: str):
    return [
        [
            InlineKeyboardButton(
                text=messages.button.common.save,
                callback_data=SaveCallback(dir=save_dir).pack(),
            ),
            InlineKeyboardButton(
                text=messages.button.common.discard,
                callback_data=CancelCallback(dir=cancel_dir).pack(),
            ),
        ]
    ]


def crud_rows(dir: str):
    return [
        [
            InlineKeyboardButton(
                text=messages.button.common.create, callback_data=f"{dir}.{CREATE}"
            ),
            InlineKeyboardButton(
                text=messages.button.common.get, callback_data=f"{dir}.{GET}"
            ),
        ],
        [
            InlineKeyboardButton(
                text=messages.button.common.update, callback_data=f"{dir}.{UPDATE}"
            ),
            InlineKeyboardButton(
                text=messages.button.common.delete, callback_data=f"{dir}.{DELETE}"
            ),
        ],
    ]


def list_row(dir: str):
    return [
        [
            InlineKeyboardButton(
                text=messages.button.common.list, callback_data=f"{dir}.{LIST}"
            )
        ]
    ]


class EditCallback(CallbackData, prefix="edt"):
    dir: str
    field: str


@dataclass
class FieldButton:
    title: str
    callback: str


def field_rows(dir: str, cancel_dir: str, fields: list[FieldButton]):
    field_rows = [
        [
            InlineKeyboardButton(
                text=field.title,
                callback_data=EditCallback(dir=dir, field=field.callback).pack(),
            )
        ]
        for field in fields
    ]
    return field_rows + save_row(dir, cancel_dir)


class PaginPageCallback(CallbackData, prefix="pgp"):
    dir: str
    page: int


def pagin_page_row(dir: str, has_prev: bool, has_next: bool):
    result = []
    if has_prev:
        result.append(
            InlineKeyboardButton(
                text=messages.button.common.previous,
                callback_data=PaginPageCallback(dir=dir, page=-1).pack(),
            )
        )
    if has_next:
        result.append(
            InlineKeyboardButton(
                text=messages.button.common.next,
                callback_data=PaginPageCallback(dir=dir, page=1).pack(),
            )
        )
    return [result]


class PaginSizeCallback(CallbackData, prefix="pgs"):
    dir: str
    size: int


def pagin_size_row(dir: str, sizes: list[int], current: int):
    return [
        [
            InlineKeyboardButton(
                text=f"{size}",
                callback_data=PaginSizeCallback(dir=dir, size=size).pack(),
            )
            for size in sizes
            if size != current
        ]
    ]


class PaginOrderCallback(CallbackData, prefix="pgo"):
    dir: str
    column: str


def pagin_order_row(dir: str, columns: list[str], current: str, ascending: bool):
    direction_emoji = (
        messages.button.common.ascending
        if ascending
        else messages.button.common.descending
    )
    return [
        [
            InlineKeyboardButton(
                text=f"{direction_emoji} {c.upper()}" if c == current else c,
                callback_data=PaginOrderCallback(dir=dir, column=c).pack(),
            )
            for c in columns
        ]
    ]
