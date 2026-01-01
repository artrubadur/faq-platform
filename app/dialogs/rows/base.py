from dataclasses import dataclass
from enum import Enum

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton

from app.core.constants.dirs import CREATE, DELETE, GET, UPDATE
from app.core.constants.emojis import EmojiAction, EmojiNav, EmojiStatus


class CloseCallback(CallbackData, prefix="cls"):
    pass


def close_row():
    return [
        [
            InlineKeyboardButton(
                text=f"{EmojiNav.CLOSE} Close", callback_data=CloseCallback().pack()
            )
        ]
    ]


class BackCallback(CallbackData, prefix="bck"):
    dir: str


def back_row(dir: str):
    return [
        [
            InlineKeyboardButton(
                text=f"{EmojiNav.BACK} Back", callback_data=BackCallback(dir=dir).pack()
            ),
        ]
    ]


class CancelCallback(CallbackData, prefix="cnc"):
    dir: str


def cancel_row(dir: str):
    return [
        [
            InlineKeyboardButton(
                text=f"{EmojiNav.CANCEL} Cancel",
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
                text=EmojiStatus.CONFIRM,
                callback_data=ConfirmCallback(dir=confirm_dir, step=step).pack(),
            ),
            InlineKeyboardButton(
                text=EmojiNav.REJECT,
                callback_data=CancelCallback(dir=cancel_dir).pack(),
            ),
        ]
    ]


class SaveCallback(CallbackData, prefix="sav"):
    dir: str


def save_row(save_dir: str, cancel_dir: str, step: str = ""):
    return [
        [
            InlineKeyboardButton(
                text=EmojiAction.SAVE, callback_data=SaveCallback(dir=save_dir).pack()
            ),
            InlineKeyboardButton(
                text=EmojiNav.CANCEL_CHANGES,
                callback_data=CancelCallback(dir=cancel_dir).pack(),
            ),
        ]
    ]


def crud_rows(dir: str):
    return [
        [
            InlineKeyboardButton(
                text=f"{EmojiAction.CREATE} Create", callback_data=f"{dir}.{CREATE}"
            ),
            InlineKeyboardButton(
                text=f"{EmojiAction.GET} Get", callback_data=f"{dir}.{GET}"
            ),
        ],
        [
            InlineKeyboardButton(
                text=f"{EmojiAction.UPDATE} Update", callback_data=f"{dir}.{UPDATE}"
            ),
            InlineKeyboardButton(
                text=f"{EmojiAction.DELETE} Delete", callback_data=f"{dir}.{DELETE}"
            ),
        ],
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
                text=EmojiNav.LEFT,
                callback_data=PaginPageCallback(dir=dir, page=-1).pack(),
            )
        )
    if has_next:
        result.append(
            InlineKeyboardButton(
                text=EmojiNav.RIGHT,
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


def pagin_order_row(dir: str, column_enum: type[Enum], current: str):
    return [
        [
            InlineKeyboardButton(
                text=col.name,
                callback_data=PaginOrderCallback(dir=dir, column=col.value).pack(),
            )
            for col in column_enum
            if col.value != current
        ]
    ]


class PaginDirectionCallback(CallbackData, prefix="pgd"):
    dir: str
    ascending: bool


def pagin_direction_row(dir: str, current: bool):
    return [
        [
            InlineKeyboardButton(
                text=(
                    EmojiNav.DOWN if current else EmojiNav.UP
                ),  # if current is ascending
                callback_data=PaginDirectionCallback(
                    dir=dir, ascending=(not current)
                ).pack(),
            )
        ]
    ]
