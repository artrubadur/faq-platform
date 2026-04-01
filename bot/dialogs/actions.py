from enum import Enum
from functools import wraps
from typing import Awaitable, Callable, Concatenate, ParamSpec

from aiogram.types import Message

from bot.dispatch.instance import bot

P = ParamSpec("P")


class SendAction(str, Enum):
    ANSWER = "answer"
    EDIT = "edit"
    REPLY = "reply"


async def send_via_action(
    message: Message, action: SendAction, *args, **kwargs
) -> Message:
    match action:
        case SendAction.EDIT:
            return await message.edit_text(
                *args, **kwargs
            )  # pyright: ignore[reportReturnType]
        case SendAction.REPLY:
            return await message.reply(*args, **kwargs)
        case _:
            return await message.answer(*args, **kwargs)


def with_message_action(
    func: Callable[Concatenate[Callable, P], Awaitable[Message]],
) -> Callable[Concatenate[Message, SendAction, P], Awaitable[Message]]:

    @wraps(func)
    async def inner(message: Message, action: SendAction, *args, **kwargs):
        async def send(*send_args, **send_kwargs):
            return await send_via_action(message, action, *send_args, **send_kwargs)

        return await func(
            send,
            *args,
            **kwargs,
        )

    return inner


async def send_via_chat(id: int, **kwargs) -> Message:
    return await bot.send_message(id, **kwargs)


def with_chat_message(
    func: Callable[Concatenate[Callable, P], Awaitable[Message]],
) -> Callable[Concatenate[int, P], Awaitable[Message]]:
    @wraps(func)
    async def inner(id: int, *args, **kwargs):
        async def send(**data):
            return await send_via_chat(id, **data)

        return await func(
            send,
            *args,
            **kwargs,
        )

    return inner
