from enum import Enum

from aiogram.types import Message


class SendAction(str, Enum):
    ANSWER = "answer"
    EDIT = "edit"


async def do_action(message: Message, action: SendAction, **kwargs):
    match action:
        case SendAction.EDIT:
            await message.edit_text(**kwargs)
        case _:
            await message.answer(**kwargs)


# def action_wrapper(func):
#     @wraps(func)
#     async def inner(message: Message, action: SendAction, *args, **kwargs):
#         async def send(**kwargs):
#             await do_action(message, action, **kwargs)
#         await func(send=send, *args, **kwargs)
#     return inner
