from typing import Awaitable, Callable

from aiogram.types import InlineKeyboardMarkup, Message

import bot.dialogs.rows.common as rows
from bot.core.customization import messages
from bot.dialogs.actions import with_message_action
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
