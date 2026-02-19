from typing import Awaitable, Callable

from aiogram.types import InlineKeyboardMarkup, Message

import app.dialogs.markups.user as mu
import app.dialogs.rows.common as brows
import app.dialogs.rows.user as urows
from app.core.messages import messages
from app.dialogs.actions import with_message_action
from app.repositories.users import UserColumn
from app.storage.models.user import User
from app.utils.format.output import (
    format_edited_user,
    format_exception,
    format_id,
    format_user,
    format_user_table,
    format_username,
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
        text=messages.responses.admin.user.enter.identity,
        parse_mode=messages.parse_mode,
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
        text=messages.responses.admin.user.enter.username,
        parse_mode=messages.parse_mode,
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
        text=messages.responses.admin.user.enter.role,
        parse_mode=messages.parse_mode,
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
        text=messages.responses.admin.user.creation.confirm.format(
            user=format_user(id=id, username=username, role=role)
        ),
        parse_mode=messages.parse_mode,
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
        text=messages.responses.admin.user.creation.successful.format(
            user=format_user(id=id, username=username, role=role)
        ),
        parse_mode=messages.parse_mode,
        reply_markup=mu.back,
    )


@with_message_action
async def send_already_exists(
    send: Callable[..., Awaitable[Message]], id: int, username: str | None
) -> Message:
    return await send(
        text=format_exception(
            messages.exceptions.user.already_exists,
            id=format_id(id),
            username=format_username(username),
        ),
        parse_mode=messages.parse_mode,
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
        text=messages.responses.admin.user.finding.successful.format(
            user=format_user(id=id, username=username, role=role)
        ),
        parse_mode=messages.parse_mode,
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
        text=messages.responses.admin.user.finding.partially_found.format(
            user=format_user(id=id, username=username, role=role)
        ),
        parse_mode=messages.parse_mode,
        reply_markup=mu.back,
    )


@with_message_action
async def send_not_found(
    send: Callable[..., Awaitable[Message]], id: int, username: str | None = None
) -> Message:
    return await send(
        text=format_exception(
            messages.exceptions.user.not_found,
            identity=(
                format_username(username) if username is not None else format_id(id)
            ),
        ),
        parse_mode=messages.parse_mode,
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
        text=messages.responses.admin.user.deletion.confirm.format(
            user=format_user(id=id, username=username, role=role)
        ),
        parse_mode=messages.parse_mode,
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
        text=messages.responses.admin.user.deletion.successful.format(
            user=format_user(id=id, username=username, role=role)
        ),
        parse_mode=messages.parse_mode,
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
        text=messages.responses.admin.user.update.confirm.format(
            user=format_user(id=id, username=username, role=role)
        ),
        parse_mode=messages.parse_mode,
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
        text=messages.responses.admin.user.update.select_field.format(
            user=changes_text
        ),
        parse_mode=messages.parse_mode,
        reply_markup=mu.field_save_update,
    )


@with_message_action
async def send_successfully_updated(
    send: Callable[..., Awaitable[Message]],
    id: int,
    username: str | None,
    role: str,
) -> Message:
    return await send(
        text=messages.responses.admin.user.update.successful.format(
            user=format_user(id=id, username=username, role=role)
        ),
        parse_mode=messages.parse_mode,
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
    text = messages.responses.admin.user.listing.successful.format(
        page=page, max_page=max_page, content=table
    )

    return await send(
        text=text,
        reply_markup=reply_markup,
        parse_mode=messages.parse_mode,
    )


@with_message_action
async def send_empty_pagination(
    send: Callable[..., Awaitable[Message]],
) -> Message:
    return await send(
        text=messages.responses.admin.user.listing.not_found,
        reply_markup=mu.back,
        parse_mode=messages.parse_mode,
    )
