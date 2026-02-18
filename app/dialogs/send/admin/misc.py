from json import dumps
from typing import Any, Awaitable, Callable

from aiogram.types import InlineKeyboardMarkup, Message

import app.dialogs.rows.root as rows
from app.core.messages import messages
from app.dialogs.actions import with_message_action
from app.utils.format.output import format_exception


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
