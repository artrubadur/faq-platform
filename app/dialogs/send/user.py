from typing import Awaitable, Callable

from aiogram.types import InlineKeyboardMarkup, Message

import app.dialogs.markups.user as mu
import app.dialogs.rows.base as rows
import app.dialogs.rows.user as urows
from app.core.constants.emoji import EmojiAction, EmojiStatus
from app.dialogs.actions import action_wrapper
from app.utils.format.output import format_edited_user, format_exception, format_user


# Input
@action_wrapper
async def send_enter_identity(
    send: Callable[..., Awaitable[Message]],
    dir: str,
    found_user_id: int | None = None,
    found_username: str | None = None,
    sender_id: int | None = None,
    sender_username: str | None = None,
) -> Message:
    reply_markup = InlineKeyboardMarkup(
        inline_keyboard=urows.identity_rows(
            dir, found_user_id, found_username, sender_id, sender_username
        )
    )
    return await send(
        text=f"{EmojiAction.ENTER} Enter a telegram id, share contact or forward a message",
        reply_markup=reply_markup,
    )


@action_wrapper
async def send_enter_username(
    send: Callable[..., Awaitable[Message]],
    dir: str,
    found_username: str | None = None,
    sender_username: str | None = None,
) -> Message:
    reply_markup = InlineKeyboardMarkup(
        inline_keyboard=urows.username_rows(dir, found_username, sender_username, empty=True)
    )
    return await send(
        text=f"{EmojiAction.ENTER} Enter a username",
        reply_markup=reply_markup,
    )


@action_wrapper
async def send_select_role(
    send: Callable[..., Awaitable[Message]], dir: str
) -> Message:
    reply_markup = InlineKeyboardMarkup(inline_keyboard=urows.role_rows(dir))
    return await send(
        text=f"{EmojiAction.SELECT} Select a role:",
        reply_markup=reply_markup,
    )


# Creation
@action_wrapper
async def send_confirm_creation(
    send: Callable[..., Awaitable[Message]],
    id: int,
    username: str | None,
    role: str,
) -> Message:
    return await send(
        text=f"{EmojiAction.SELECT} Confirm creation?\n{format_user(id=id, username=username, role=role)}",
        parse_mode="HTML",
        reply_markup=mu.confirm_creation,
    )


@action_wrapper
async def send_successfully_created(
    send: Callable[..., Awaitable[Message]],
    id: int,
    username: str | None,
    role: str,
) -> Message:
    return await send(
        text=f"{EmojiStatus.SUCCESSFUL} User has been successfully created:\n{format_user(id=id, username=username, role=role)}",
        parse_mode="HTML",
        reply_markup=mu.back,
    )


@action_wrapper
async def send_failed_creation(
    send: Callable[..., Awaitable[Message]],
    exception="Unexcepted error.",
) -> Message:
    return await send(
        text=format_exception(f"Failed to create the user: {exception}"),
        reply_markup=mu.back,
    )


# Finding
@action_wrapper
async def send_successfully_found(
    send: Callable[..., Awaitable[Message]],
    id: int,
    username: str | None,
    role: str,
) -> Message:
    return await send(
        text=(
            f"{EmojiStatus.SUCCESSFUL} The user has been successfully found in the database:\n"
            f"{format_user(id=id, username=username, role=role)}"
        ),
        parse_mode="HTML",
        reply_markup=mu.back,
    )


@action_wrapper
async def send_partially_found(
    send: Callable[..., Awaitable[Message]],
    id: int,
    username: str | None = None,
    role: str | None = None,
) -> Message:
    return await send(
        text=(
            f"{EmojiStatus.WARNING} The user has been partially found but missing in the database:\n"
            f"{format_user(id=id, username=username, role=role)}"
        ),
        parse_mode="HTML",
        reply_markup=mu.back,
    )


@action_wrapper
async def send_not_found(
    send: Callable[..., Awaitable[Message]], id: int, username: str | None = None
) -> Message:
    return await send(
        text=f"{EmojiStatus.FAILED} User {username or id}` not found",
        parse_mode="Markdown",
        reply_markup=mu.back,
    )


# Deletion
@action_wrapper
async def send_confirm_deletion(
    send: Callable[..., Awaitable[Message]],
    id: int,
    username: str | None,
    role: str,
) -> Message:
    return await send(
        text=f"{EmojiAction.SELECT} Confirm deletion?\n{format_user(id=id, username=username, role=role)}",
        parse_mode="HTML",
        reply_markup=mu.confirm_deletion,
    )


@action_wrapper
async def send_successfully_deleted(
    send: Callable[..., Awaitable[Message]],
    id: int,
    username: str | None,
    role: str,
) -> Message:
    return await send(
        text=f"{EmojiStatus.SUCCESSFUL} Next user has been successfully deleted:\n{format_user(id=id, username=username, role=role)}",
        parse_mode="HTML",
        reply_markup=mu.back,
    )


# Update
@action_wrapper
async def send_confirm_update(
    send: Callable[..., Awaitable[Message]],
    id: int,
    username: str | None,
    role: str,
) -> Message:
    return await send(
        text=f"{EmojiAction.SELECT} Update this user?\n{format_user(id=id, username=username, role=role)}",
        parse_mode="HTML",
        reply_markup=mu.confirm_update,
    )


@action_wrapper
async def send_changes(
    send: Callable[..., Awaitable[Message]],
    id: int,
    edited_id: int,
    username: str | None,
    edited_username: str | None,
    role: str,
    edited_role: str,
) -> Message:
    changes_text = format_edited_user(
        id, edited_id, username, edited_username, role, edited_role
    )
    return await send(
        text=f"{changes_text}{EmojiAction.SELECT} Select the field to edit:",
        parse_mode="HTML",
        reply_markup=mu.field_save_update,
    )


@action_wrapper
async def send_edit_username(
    send: Callable[..., Awaitable[Message]],
    dir: str,
    found_username: str | None = None,
) -> Message:
    reply_markup = InlineKeyboardMarkup(
        inline_keyboard=urows.username_rows(dir, found_username, empty=True)
        + rows.cancel_row("settings.users.update")
    )

    return await send(
        text=f"{EmojiAction.ENTER} Enter the username",
        reply_markup=reply_markup,
    )


@action_wrapper
async def send_edit_role(
    send: Callable[..., Awaitable[Message]],
    dir: str,
) -> Message:
    reply_markup = InlineKeyboardMarkup(
        inline_keyboard=urows.role_rows(dir) + rows.cancel_row("settings.users.update")
    )

    return await send(
        text=f"{EmojiAction.ENTER} Select the role:",
        reply_markup=reply_markup,
    )


@action_wrapper
async def send_successfully_updated(
    send: Callable[..., Awaitable[Message]],
    id: int,
    username: str | None,
    role: str,
) -> Message:
    return await send(
        text=f"{EmojiStatus.SUCCESSFUL} The qser has been successfully updated:\n{format_user(id=id, username=username, role=role)}",
        parse_mode="HTML",
        reply_markup=mu.back,
    )


@action_wrapper
async def send_failed_update(
    send: Callable[..., Awaitable[Message]],
    exception="Unexcepted error.",
) -> Message:
    return await send(
        text=format_exception(f"Failed to update the user: {exception}"),
        reply_markup=mu.back,
    )
