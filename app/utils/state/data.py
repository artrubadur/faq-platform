from typing import Any

from aiogram import Bot, Dispatcher

from app.bot.storage import StorageScope
from app.utils.state.storage import get_key, get_storage


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
