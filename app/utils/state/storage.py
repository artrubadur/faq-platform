from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.base import StorageKey

from app.bot.storage import LSTStorage


def get_storage(dispatcher: Dispatcher) -> LSTStorage:
    return dispatcher.fsm.storage  # pyright: ignore[reportReturnType]


def get_key(bot: Bot, target_id: int):
    return StorageKey(bot_id=bot.id, chat_id=target_id, user_id=target_id)


# async def clear_storage(
#     bot: Bot, dispatcher: Dispatcher, target_id: int, scope: StorageScope
# ):
#     storage = get_storage(dispatcher)
#     key = get_key(bot, target_id)
#     await storage.clear(key, scope)


# async def clear_storage(state: LSTContext, scope: StorageScope = "short"):
#     await state.storage.clear(state.key, scope)
