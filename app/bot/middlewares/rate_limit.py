import time

from loguru import logger
from redis.asyncio import Redis

from app.bot.handlers.common import rate_limit_handler
from app.bot.middlewares.access import AccessMiddleware
from app.storage.models.user import Role


class RateLimitMiddleware(AccessMiddleware):
    def __init__(
        self,
        redis: Redis,
        max_requests: int,
        window: int,
        skip_admin: bool = True,
    ) -> None:
        self.redis = redis
        self.max_requests = max_requests
        self.window = window
        self.skip_admin = skip_admin

    async def _is_limit_exceeded(self, sender_id: int) -> bool:
        bucket = int(time.time() // self.window)
        key = f"rate_limit:{sender_id}:{bucket}"

        current = await self.redis.incr(key)
        if current == 1:
            await self.redis.expire(key, self.window)

        return current > self.max_requests

    async def __call__(self, handler, event, data):
        sender_id = event.from_user.id

        if self.skip_admin:
            sender_role = await self._resolve_role(data, sender_id)
            if sender_role == Role.ADMIN:
                return await handler(event, data)

        if await self._is_limit_exceeded(sender_id):
            logger.debug(
                "Handler denied: sender exceeded rate limit",
                tg_id=sender_id,
                limit=self.max_requests,
                window_sec=self.window,
            )
            await rate_limit_handler(event)  # pyright: ignore[reportArgumentType]
            return

        return await handler(event, data)
