from typing import Any, Dict, Literal

from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import (
    BaseStorage,
    DefaultKeyBuilder,
    StateType,
    StorageKey,
)
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

StorageScope = Literal["long", "short"]


class TempStorage(BaseStorage):
    def __init__(self, redis: Redis, long_ttl: int, short_ttl: int) -> None:
        self.storage_scopes: dict[StorageScope, RedisStorage] = {
            "long": RedisStorage(
                redis=redis,
                state_ttl=long_ttl,
                data_ttl=long_ttl,
                key_builder=DefaultKeyBuilder(prefix="fsm:long"),
            ),
            "short": RedisStorage(
                redis=redis,
                state_ttl=short_ttl,
                data_ttl=short_ttl,
                key_builder=DefaultKeyBuilder(prefix="fsm:short"),
            ),
        }

    async def close(self) -> None:
        for storage in self.storage_scopes.values():
            await storage.close()

    async def set_state(
        self, key: StorageKey, state: StateType = None, scope: StorageScope = "short"
    ):
        storage = self.storage_scopes[scope]
        return await storage.set_state(key, state)

    async def get_state(self, key: StorageKey, scope: StorageScope = "short"):
        storage = self.storage_scopes[scope]
        return await storage.get_state(key)

    async def set_data(
        self, key: StorageKey, data: Dict[str, Any], scope: StorageScope = "short"
    ):
        storage = self.storage_scopes[scope]
        await storage.set_data(key, data)

    async def get_data(self, key: StorageKey, scope: StorageScope = "short"):
        storage = self.storage_scopes[scope]
        return await storage.get_data(key)

    async def get_value(
        self,
        key: StorageKey,
        dict_key: str,
        default: Any = None,
        scope: StorageScope = "short",
    ):
        storage = self.storage_scopes[scope]
        return await storage.get_value(key, dict_key, default)

    async def update_data(
        self, key: StorageKey, data: dict[str, Any], scope: StorageScope = "short"
    ) -> dict[str, Any]:
        current_data = await self.get_data(key, scope)
        current_data.update(data)
        await self.set_data(key, current_data, scope)
        return current_data

    async def clear(self, key: StorageKey, scope: StorageScope = "short"):
        await self.set_data(key, {}, scope)
        await self.set_state(key, None, scope)


class TempContext(FSMContext):
    storage: TempStorage

    def __init__(self, storage: TempStorage, key: StorageKey) -> None:
        super().__init__(storage, key)

    async def clear(self):
        await self.storage.clear(self.key)
