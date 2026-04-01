from aiogram import BaseMiddleware
from loguru import logger

from bot.dispatch.handlers.common import banned_handler
from bot.services.user.gateway import user_gateway
from bot.utils.state.temp import TempContext
from shared.contracts.user.responses import Role
from shared.http.exceptions import NotFoundError


class AccessMiddleware(BaseMiddleware):
    async def _resolve_role(self, data: dict, sender_id: int) -> str:
        state: TempContext = data["state"]

        if cached_role := await self._resolve_cached_role(state):
            return cached_role

        stored_role = await self._resolve_stored_role(sender_id)
        await state.storage.update_data(state.key, {"sender_role": stored_role}, "long")
        return stored_role

    async def _resolve_cached_role(self, state: TempContext) -> str:
        return await state.storage.get_value(state.key, "sender_role", None, "long")

    async def _resolve_stored_role(self, sender_id: int) -> str:
        try:
            user = await user_gateway.get_user(sender_id)
            return user.role
        except NotFoundError:
            return Role.USER


class AdminMiddleware(AccessMiddleware):
    async def __call__(self, handler, event, data):
        sender_id = event.from_user.id
        sender_role = await self._resolve_stored_role(sender_id)

        if sender_role != Role.ADMIN:
            logger.debug(
                "Handler skipped: sender is not admin",
                tg_id=sender_id,
            )
            return

        return await handler(event, data)


class BannedMiddleware(AccessMiddleware):
    async def __call__(self, handler, event, data):
        sender_id = event.from_user.id
        sender_role = await self._resolve_role(data, sender_id)

        if sender_role == Role.BANNED:
            logger.debug(
                "Handler denied: sender is banned",
                tg_id=sender_id,
            )
            await banned_handler(event)  # pyright: ignore[reportArgumentType]
            return

        return await handler(event, data)
