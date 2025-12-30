from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton

from app.core.constants.emoji import EmojiAction, EmojiNav, EmojiStatus


class CloseCallback(CallbackData, prefix="close"):
    pass


def close_row():
    return [
        [
            InlineKeyboardButton(
                text=f"{EmojiNav.CLOSE} Close", callback_data=CloseCallback().pack()
            )
        ]
    ]


class BackCallback(CallbackData, prefix="back"):
    dir: str


def back_row(dir: str):
    return [
        [
            InlineKeyboardButton(
                text=f"{EmojiNav.BACK} Back", callback_data=BackCallback(dir=dir).pack()
            ),
        ]
    ]


class CancelCallback(CallbackData, prefix="cancel"):
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


class ConfirmCallback(CallbackData, prefix="confirm"):
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


class SaveCallback(CallbackData, prefix="save"):
    dir: str


def save_row(save_dir: str, cancel_dir: str):
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
                text=f"{EmojiAction.CREATE} Create", callback_data=f"{dir}.create"
            ),
            InlineKeyboardButton(
                text=f"{EmojiAction.GET} Get", callback_data=f"{dir}.get"
            ),
        ],
        [
            InlineKeyboardButton(
                text=f"{EmojiAction.UPDATE} Update", callback_data=f"{dir}.update"
            ),
            InlineKeyboardButton(
                text=f"{EmojiAction.DELETE} Delete", callback_data=f"{dir}.delete"
            ),
        ],
    ]


class EditCallback(CallbackData, prefix="edit"):
    dir: str
    field: str


def field_rows(dir, cancel_dir: str, fields: list):
    field_rows = [
        [
            InlineKeyboardButton(
                text=field.capitalize(),
                callback_data=EditCallback(dir=dir, field=field).pack(),
            )
        ]
        for field in fields
    ]
    return field_rows + save_row(dir, cancel_dir)


# def edit_row(dir, suggestions, nullable):
#     return cancel_row(dir) +
