from typing import Awaitable, Callable

from aiogram.types import Message

from bot.core.customization.commands import commands
from bot.dialogs.actions import with_message_action
from bot.utils.format.output import format_response


@with_message_action
async def send_command(
    send: Callable[..., Awaitable[Message]], message: Message, text: str
) -> Message:
    return await send(
        text=format_response(text, message), parse_mode=commands.parse_mode
    )
