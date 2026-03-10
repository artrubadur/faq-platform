from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton

import app.dialogs.rows.common as rows
from app.core.constants.dirs import USERS
from app.core.messages import messages
from app.storage.models.user import Role

cancel_row = rows.cancel_row(USERS[1])


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
                    text=messages.button.user.found.format(
                        identity=(
                            f"@{found_username}"
                            if found_username is not None
                            else found_user_id
                        )
                    ),
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
                    text=messages.button.user.you.format(
                        identity=(
                            f"@{sender_username}"
                            if sender_username is not None
                            else sender_id
                        )
                    ),
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
                    text=messages.button.user.found.format(identity=found_username),
                    callback_data=callback_data,
                )
            ]
        )
    if sender_username is not None:
        callback_data = UsernameCallback(dir=dir, username=sender_username).pack()
        rows.append(
            [
                InlineKeyboardButton(
                    text=messages.button.user.you.format(identity=sender_username),
                    callback_data=callback_data,
                )
            ]
        )
    if empty:
        callback_data = UsernameCallback(dir=dir, username=None).pack()
        rows.append(
            [
                InlineKeyboardButton(
                    text=messages.button.common.empty, callback_data=callback_data
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
        for role in ["banned", "user"]
    ]
