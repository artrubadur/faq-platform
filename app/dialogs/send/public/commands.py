from typing import Awaitable, Callable

from aiogram.types import Message

from app.dialogs.actions import with_message_action
from app.utils.format.output import format_response


@with_message_action
async def send_command(
    send: Callable[..., Awaitable[Message]], message: Message, text: str
) -> Message:
    return await send(text=format_response(text, message), parse_mode="HTML")
