from typing import Awaitable, Callable

from aiogram.types import Message, ReplyKeyboardRemove

from app.dialogs.actions import with_message_action


@with_message_action
async def send_start(
    send: Callable[..., Awaitable[Message]], full_name: str
) -> Message:
    return await send(
        text=f"You started the bot, {full_name}!",
        reply_markup=ReplyKeyboardRemove(),
    )
