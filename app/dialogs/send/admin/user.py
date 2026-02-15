from typing import Awaitable, Callable

from aiogram.types import InlineKeyboardMarkup, Message

import app.dialogs.markups.user as mu
import app.dialogs.rows.common as brows
import app.dialogs.rows.user as urows
from app.core.constants.emojis import EmojiAction, EmojiStatus
from app.dialogs.actions import with_message_action
from app.repositories.users import UserColumn
from app.storage.models.user import User
from app.utils.format.output import (
    format_edited_user,
    format_exception,
    format_user,
    format_user_table,
)


# Input
@with_message_action
async def send_enter_identity(
    send: Callable[..., Awaitable[Message]],
    cancel_dir: str,
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
        + brows.cancel_row(cancel_dir)
    )
    return await send(
        text=f"{EmojiAction.ENTER} Enter a telegram id, share contact or forward a message",
        reply_markup=reply_markup,
    )


@with_message_action
async def send_enter_username(
    send: Callable[..., Awaitable[Message]],
    cancel_dir: str,
    dir: str,
    found_username: str | None = None,
    sender_username: str | None = None,
) -> Message:
    reply_markup = InlineKeyboardMarkup(
        inline_keyboard=urows.username_rows(
            dir, found_username, sender_username, empty=True
        )
        + brows.cancel_row(cancel_dir)
    )
    return await send(
        text=f"{EmojiAction.ENTER} Enter a username",
        reply_markup=reply_markup,
    )


@with_message_action
async def send_select_role(
    send: Callable[..., Awaitable[Message]], cancel_dir: str, dir: str
) -> Message:
    reply_markup = InlineKeyboardMarkup(
        inline_keyboard=urows.role_rows(dir) + brows.cancel_row(cancel_dir)
    )
    return await send(
        text=f"{EmojiAction.SELECT} Select a role:",
        reply_markup=reply_markup,
    )


# Creation
@with_message_action
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


@with_message_action
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


@with_message_action
async def send_failed_creation(
    send: Callable[..., Awaitable[Message]],
    exception="Unexcepted error.",
) -> Message:
    return await send(
        text=format_exception(f"Failed to create the user: {exception}"),
        reply_markup=mu.back,
    )


# Finding
@with_message_action
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


@with_message_action
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


@with_message_action
async def send_not_found(
    send: Callable[..., Awaitable[Message]], id: int, username: str | None = None
) -> Message:
    return await send(
        text=f"{EmojiStatus.FAILED} User `{username or id}` not found",
        parse_mode="Markdown",
        reply_markup=mu.back,
    )


# Deletion
@with_message_action
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


@with_message_action
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
@with_message_action
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


@with_message_action
async def send_changes(
    send: Callable[..., Awaitable[Message]],
    id: int,
    username: str | None,
    edited_username: str | None,
    role: str,
    edited_role: str,
) -> Message:
    changes_text = format_edited_user(id, username, edited_username, role, edited_role)
    return await send(
        text=f"{changes_text}{EmojiAction.SELECT} Select the field to edit:",
        parse_mode="HTML",
        reply_markup=mu.field_save_update,
    )


@with_message_action
async def send_edit_username(
    send: Callable[..., Awaitable[Message]],
    dir: str,
    found_username: str | None = None,
) -> Message:
    reply_markup = InlineKeyboardMarkup(
        inline_keyboard=urows.username_rows(dir, found_username, empty=True)
        + brows.cancel_row(dir)
    )

    return await send(
        text=f"{EmojiAction.ENTER} Enter the username",
        reply_markup=reply_markup,
    )


@with_message_action
async def send_edit_role(
    send: Callable[..., Awaitable[Message]],
    dir: str,
) -> Message:
    reply_markup = InlineKeyboardMarkup(
        inline_keyboard=urows.role_rows(dir) + brows.cancel_row(dir)
    )

    return await send(
        text=f"{EmojiAction.ENTER} Select the role:",
        reply_markup=reply_markup,
    )


@with_message_action
async def send_successfully_updated(
    send: Callable[..., Awaitable[Message]],
    id: int,
    username: str | None,
    role: str,
) -> Message:
    return await send(
        text=f"{EmojiStatus.SUCCESSFUL} The user has been successfully updated:\n{format_user(id=id, username=username, role=role)}",
        parse_mode="HTML",
        reply_markup=mu.back,
    )


@with_message_action
async def send_failed_update(
    send: Callable[..., Awaitable[Message]],
    exception="Unexcepted error.",
) -> Message:
    return await send(
        text=format_exception(f"Failed to update the user: {exception}"),
        reply_markup=mu.back,
    )


@with_message_action
async def send_pagination(
    send: Callable[..., Awaitable[Message]],
    users: list[User],
    order: str,
    ascending: bool,
    page: int,
    max_page: int,
    page_size: int,
) -> Message:

    has_prev = page > 1
    has_next = page != max_page
    index_offset = (page - 1) * page_size

    columns = [m.value for m in UserColumn]

    reply_markup = mu.make_listing_markup(
        columns, order, ascending, page_size, has_prev, has_next
    )

    table = format_user_table(users, columns, index_offset)
    text = f"{EmojiAction.LIST} User list: {page}/{max_page}\n```\n{table}\n```"

    return await send(text=text, reply_markup=reply_markup, parse_mode="Markdown")


@with_message_action
async def send_empty_pagination(
    send: Callable[..., Awaitable[Message]],
) -> Message:
    return await send(
        text=f"{EmojiAction.LIST} No users found in the system", reply_markup=mu.back
    )
