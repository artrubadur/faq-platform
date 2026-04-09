from typing import Awaitable, Callable

from aiogram.types import Message

from bot.core.customization.commands import commands
from bot.dialogs.actions import with_message_action
from bot.utils.config.send_text import SendText
from bot.utils.format.output import format_response


@with_message_action
async def send_command(
    send: Callable[..., Awaitable[Message]], message: Message, text: SendText
) -> Message:
    return await send(
        text=format_response(text.text, message),
        parse_mode=commands.parse_mode,
        link_preview_options=text.link_preview_options,
    )
