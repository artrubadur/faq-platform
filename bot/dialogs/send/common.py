from typing import Any, Awaitable, Callable

from aiogram.types import InlineKeyboardMarkup, Message

import bot.dialogs.rows.common as rows
from bot.core.customization import messages
from bot.dialogs.actions import with_chat_message, with_message_action
from bot.utils.format.output import format_response


@with_message_action
async def send_unexcepted_error(
    send: Callable[..., Awaitable[Message]], message: Message
) -> Message:
    return await send(
        text=format_response(messages.responses.public.error, message),
        parse_mode=messages.parse_mode,
    )


@with_message_action
async def send_banned(
    send: Callable[..., Awaitable[Message]], message: Message
) -> Message:
    return await send(
        text=format_response(messages.responses.public.banned, message),
        parse_mode=messages.parse_mode,
    )


@with_message_action
async def send_rate_limit(
    send: Callable[..., Awaitable[Message]], message: Message
) -> Message:
    return await send(
        text=format_response(messages.responses.public.rate_limited, message),
        parse_mode=messages.parse_mode,
    )


@with_message_action
async def send_invalid(
    send: Callable[..., Awaitable[Message]], cancel_dir: str, exception: str | None
) -> Message:
    reply_markup = InlineKeyboardMarkup(inline_keyboard=rows.back_row(cancel_dir))

    return await send(
        text=messages.responses.admin.invalid.format(exception=exception),
        parse_mode=messages.parse_mode,
        reply_markup=reply_markup,
    )


@with_message_action
async def send_access_denied(
    send: Callable[..., Awaitable[Message]],
    cancel_dir: str | None,
    exception: str | None,
) -> Message:
    reply_markup = (
        InlineKeyboardMarkup(inline_keyboard=rows.back_row(cancel_dir))
        if cancel_dir
        else None
    )

    return await send(
        text=messages.responses.admin.access_denied.format(exception=exception),
        parse_mode=messages.parse_mode,
        reply_markup=reply_markup,
    )


@with_message_action
async def send_expired(
    send: Callable[..., Awaitable[Message]], cancel_dir: str
) -> Message:
    reply_markup = InlineKeyboardMarkup(inline_keyboard=rows.back_row(cancel_dir))

    return await send(
        text=messages.responses.admin.expired,
        parse_mode=messages.parse_mode,
        reply_markup=reply_markup,
    )


@with_chat_message
async def send_log(
    send: Callable[..., Awaitable[Message]],
    name: str,
    message: str,
    level: Any,
    exception: Exception | None,
    repeat: int | None,
    repeat_limit: int,
) -> Message:

    repeat_str = f"Repeat: {repeat}/{repeat_limit}\n" if repeat is not None else ""
    error_str = (
        f"Error: `{exception.type} {exception.value}`\n"
        if exception is not None
        else ""
    )
    return await send(
        text=(
            f"{level.icon} [{level.name}] from `{name}`\n"
            f"{repeat_str}"
            f"Log: `{message}`\n"
            f"{error_str}"
            f"Check the logs for more"
        ),
        parse_mode="MarkDown",
    )
