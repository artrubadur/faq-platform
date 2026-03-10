from typing import Any

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.base import StorageKey

from app.storage.temp import StorageScope, TempStorage


def get_storage(dispatcher: Dispatcher) -> TempStorage:
    return dispatcher.fsm.storage  # pyright: ignore[reportReturnType]


def get_key(bot: Bot, target_id: int):
    return StorageKey(bot_id=bot.id, chat_id=target_id, user_id=target_id)


async def set_data(
    bot: Bot,
    dispatcher: Dispatcher,
    target_id: int,
    data: dict[str, Any],
    scope: StorageScope,
):
    storage = get_storage(dispatcher)
    key = get_key(bot, target_id)
    await storage.set_data(key, data, scope)


async def get_data(
    bot: Bot, dispatcher: Dispatcher, target_id: int, scope: StorageScope
):
    storage = get_storage(dispatcher)
    key = get_key(bot, target_id)
    return await storage.get_data(key, scope)


async def update_data(
    bot: Bot,
    dispatcher: Dispatcher,
    target_id: int,
    data: dict[str, Any],
    scope: StorageScope,
):
    storage = get_storage(dispatcher)
    key = get_key(bot, target_id)
    return await storage.update_data(key, data, scope)


async def clear_data(
    bot: Bot, dispatcher: Dispatcher, target_id: int, scope: StorageScope
):
    await set_data(bot, dispatcher, target_id, {}, scope)
