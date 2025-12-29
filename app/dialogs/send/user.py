from aiogram.types import InlineKeyboardMarkup, Message

import app.dialogs.markups.user as mu
import app.dialogs.rows.base as brows
import app.dialogs.rows.user as urows
from app.core.constants.emoji import EmojiAction, EmojiStatus
from app.dialogs.actions import SendAction, do_action
from app.utils.format.output import (
    format_edited_user_output,
    format_exception_output,
    format_user_output,
)


# Input
async def send_enter_identity(
    message: Message,
    dir: str,
    found_id: int | None = None,
    found_username: str | None = None,
    sender_id: int | None = None,
    sender_username: str | None = None,
    *,
    action: SendAction,
):
    reply_markup = InlineKeyboardMarkup(
        inline_keyboard=urows.identity_rows(
            dir, found_id, found_username, sender_id, sender_username
        )
    )
    await do_action(
        message,
        action,
        text=f"{EmojiAction.ENTER} Enter a telegram id, share contact or forward a message",
        reply_markup=reply_markup,
    )


async def send_enter_username(
    message: Message,
    dir: str,
    found_username: str | None = None,
    sender_username: str | None = None,
    *,
    action: SendAction,
):
    reply_markup = InlineKeyboardMarkup(
        inline_keyboard=urows.username_rows(dir, found_username, sender_username)
    )
    await do_action(
        message,
        action,
        text=f"{EmojiAction.ENTER} Enter a username",
        reply_markup=reply_markup,
    )


async def send_select_role(message: Message, dir: str, *, action: SendAction):
    reply_markup = InlineKeyboardMarkup(inline_keyboard=urows.role_rows(dir))
    await do_action(
        message,
        action,
        text=f"{EmojiAction.SELECT} Select a role:",
        reply_markup=reply_markup,
    )


# Output
async def send_invalid(
    message: Message, dir: str, text: str | None, action: SendAction
):
    reply_markup = InlineKeyboardMarkup(inline_keyboard=brows.back_row(dir))
    await do_action(
        message,
        action,
        text=f"{EmojiStatus.WARNING} {text}. Retry or back",
        reply_markup=reply_markup,
    )


# Creation
async def send_confirm_creation(
    message: Message,
    id: int,
    username: str | None,
    role: str,
    *,
    action: SendAction,
):
    await do_action(
        message,
        action,
        text=f"{EmojiAction.SELECT} Confirm creation?\n{format_user_output(id=id, username=username, role=role)}",
        parse_mode="HTML",
        reply_markup=mu.confirm_creation,
    )


async def send_successfully_created(
    message: Message,
    id: int,
    username: str | None,
    role: str,
    *,
    action: SendAction,
):
    await do_action(
        message,
        action,
        text=f"{EmojiStatus.SUCCESSFUL} User has been successfully created:\n{format_user_output(id=id, username=username, role=role)}",
        parse_mode="HTML",
        reply_markup=mu.back,
    )


async def send_failed_creation(
    message: Message,
    exception="Unexcepted error.",
    *,
    action: SendAction,
):
    await do_action(
        message,
        action,
        text=format_exception_output(f"Failed to create the user: {exception}"),
        reply_markup=mu.back,
    )


# FInding
async def send_successfully_found(
    message: Message,
    id: int,
    username: str | None,
    role: str,
    *,
    action: SendAction,
):
    await do_action(
        message,
        action,
        text=(
            f"{EmojiStatus.SUCCESSFUL} The user has been successfully found in the database:\n"
            f"{format_user_output(id=id, username=username, role=role)}"
        ),
        parse_mode="HTML",
        reply_markup=mu.back,
    )


async def send_partially_found(
    message: Message,
    id: int,
    username: str | None = None,
    role: str | None = None,
    *,
    action: SendAction,
):
    await do_action(
        message,
        action,
        text=(
            f"{EmojiStatus.WARNING} The user has been partially found but missing in the database:\n"
            f"{format_user_output(id=id, username=username, role=role)}"
        ),
        parse_mode="HTML",
        reply_markup=mu.back,
    )


async def send_not_found(
    message: Message, id: int, username: str | None = None, *, action: SendAction
):
    await do_action(
        message,
        action,
        text=f"{EmojiStatus.FAILED} User {username or id}` not found",
        parse_mode="Markdown",
        reply_markup=mu.back,
    )


# Deletion
async def send_confirm_deletion(
    message: Message,
    id: int,
    username: str | None,
    role: str,
    *,
    action: SendAction,
):
    await do_action(
        message,
        action,
        text=f"{EmojiAction.SELECT} Confirm deletion?\n{format_user_output(id=id, username=username, role=role)}",
        parse_mode="HTML",
        reply_markup=mu.confirm_deletion,
    )


async def send_successfully_deleted(
    message: Message,
    id: int,
    username: str | None,
    role: str,
    *,
    action: SendAction,
):
    await do_action(
        message,
        action,
        text=f"{EmojiStatus.SUCCESSFUL} Next user has been successfully deleted:\n{format_user_output(id=id, username=username, role=role)}",
        parse_mode="HTML",
        reply_markup=mu.back,
    )


# Update
async def send_confirm_update(
    message: Message,
    id: int,
    username: str | None,
    role: str,
    *,
    action: SendAction,
):
    await do_action(
        message,
        action,
        text=f"{EmojiAction.SELECT} Update this user?\n{format_user_output(id=id, username=username, role=role)}",
        parse_mode="HTML",
        reply_markup=mu.confirm_update,
    )


async def send_changes(
    message: Message,
    id: int,
    edited_id: int,
    username: str | None,
    edited_username: str | None,
    role: str,
    edited_role: str,
    *,
    action: SendAction,
):
    changes_text = format_edited_user_output(
        id, edited_id, username, edited_username, role, edited_role
    )
    await do_action(
        message,
        action,
        text=f"{changes_text}\n{EmojiAction.SELECT} Select field to edit:",
        parse_mode="HTML",
        reply_markup=mu.field_update,
    )


async def send_edit_username(
    message: Message,
    dir: str,
    found_username: str | None = None,
    *,
    action: SendAction,
):
    reply_markup = InlineKeyboardMarkup(
        inline_keyboard=urows.username_rows(dir, found_username, clear=True)
        + brows.cancel_row("settings.users.update")
    )

    await do_action(
        message,
        action,
        text=f"{EmojiAction.ENTER} Enter a username",
        reply_markup=reply_markup,
    )


async def send_edit_role(
    message: Message,
    dir: str,
    *,
    action: SendAction,
):
    reply_markup = InlineKeyboardMarkup(
        inline_keyboard=urows.role_rows(dir) + brows.cancel_row("settings.users.update")
    )

    await do_action(
        message,
        action,
        text=f"{EmojiAction.ENTER} Select a role:",
        reply_markup=reply_markup,
    )


async def send_successfully_updated(
    message: Message,
    id: int,
    username: str | None,
    role: str,
    *,
    action: SendAction,
):
    await do_action(
        message,
        action,
        text=f"{EmojiStatus.SUCCESSFUL} User has been successfully updated:\n{format_user_output(id=id, username=username, role=role)}",
        parse_mode="HTML",
        reply_markup=mu.back,
    )


async def send_failed_update(
    message: Message,
    exception="Unexcepted error.",
    *,
    action: SendAction,
):
    await do_action(
        message,
        action,
        text=format_exception_output(f"Failed to update the user: {exception}"),
        reply_markup=mu.back,
    )
