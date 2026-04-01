from json import dumps
from typing import Any, Awaitable, Callable

from aiogram.types import InlineKeyboardMarkup, Message

import bot.dialogs.rows.root as rows
from bot.core.customization import messages
from bot.dialogs.actions import with_message_action
from bot.utils.format.output import format_exception, format_id, format_username


@with_message_action
async def send_confirm_goto(
    send: Callable[..., Awaitable[Message]], dir: str
) -> Message:
    reply_markup = InlineKeyboardMarkup(inline_keyboard=rows.go_row(dir))

    return await send(
        text=messages.responses.admin.misc.goto.confirm.format(content=dir),
        parse_mode=messages.parse_mode,
        reply_markup=reply_markup,
    )


@with_message_action
async def send_invalid_path(send: Callable[..., Awaitable[Message]]) -> Message:
    return await send(
        text=format_exception(messages.exceptions.misc.invalid_path),
        parse_mode=messages.parse_mode,
    )


@with_message_action
async def send_json(
    send: Callable[..., Awaitable[Message]], data: dict[str, Any]
) -> Message:
    str_data = dumps(data, indent=2)

    return await send(
        text=messages.responses.admin.misc.state.serialization.format(content=str_data),
        parse_mode=messages.parse_mode,
    )


@with_message_action
async def send_invalid_argument(
    send: Callable[..., Awaitable[Message]], exception: str
) -> Message:
    return await send(
        text=format_exception(
            messages.exceptions.misc.invalid_argument.format(exception=exception)
        ),
        parse_mode=messages.parse_mode,
    )


@with_message_action
async def send_banned(
    send: Callable[..., Awaitable[Message]], id: int, username: str | None
) -> Message:
    return await send(
        text=messages.responses.admin.ban.banned.format(
            identity=(
                format_username(username) if username is not None else format_id(id)
            )
        ),
        parse_mode=messages.parse_mode,
    )


@with_message_action
async def send_unbanned(
    send: Callable[..., Awaitable[Message]], identity: int, username: str | None
) -> Message:
    return await send(
        text=messages.responses.admin.ban.unbanned.format(
            identity=identity,
            username=username or messages.format.fallback.username,
        ),
        parse_mode=messages.parse_mode,
    )
