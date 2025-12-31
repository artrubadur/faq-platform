from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton

import app.dialogs.rows.base as rows
from app.core.constants.emoji import EmojiAction
from app.storage.db.models.user import Role

DIR = "settings.users"

cancel_row = rows.cancel_row(DIR)


class IdentityCallback(CallbackData, prefix="identity"):
    dir: str
    id: int
    username: str | None


def identity_rows(
    dir: str,
    found_user_id: int | None = None,
    found_username: str | None = None,
    sender_id: int | None = None,
    sender_username: str | None = None,
):
    rows = []
    if found_user_id is not None:
        callback_data = IdentityCallback(
            dir=dir, id=found_user_id, username=found_username
        ).pack()
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"Found ({found_username or found_user_id})",
                    callback_data=callback_data,
                )
            ]
        )
    if sender_id is not None:
        callback_data = IdentityCallback(
            dir=dir, id=sender_id, username=sender_username
        ).pack()
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"Me ({sender_username or sender_id})",
                    callback_data=callback_data,
                )
            ]
        )
    return rows


class UsernameCallback(CallbackData, prefix="username"):
    dir: str
    username: str | None


def username_rows(
    dir: str,
    found_username: str | None = None,
    sender_username: str | None = None,
    empty=False,
):
    rows = []
    if found_username is not None:
        callback_data = UsernameCallback(dir=dir, username=found_username).pack()
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"Found ({found_username})", callback_data=callback_data
                )
            ]
        )
    if sender_username is not None:
        callback_data = UsernameCallback(dir=dir, username=sender_username).pack()
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"Me ({sender_username})", callback_data=callback_data
                )
            ]
        )
    if empty:
        callback_data = UsernameCallback(dir=dir, username=None).pack()
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"{EmojiAction.EMPTY} Empty", callback_data=callback_data
                )
            ]
        )

    return rows


class RoleCallback(CallbackData, prefix="role"):
    dir: str
    role: str


def role_rows(dir: str):
    return [
        [
            InlineKeyboardButton(
                text=role.value.upper(),
                callback_data=RoleCallback(dir=dir, role=role).pack(),
            )
        ]
        for role in Role
    ]
