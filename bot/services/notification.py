from typing import Callable

from aiogram.exceptions import TelegramForbiddenError
from loguru import logger

from bot.services.api.schemas.user import Role
from bot.services.user.gateway import user_gateway


class NotificationService:
    async def notify(self, role: Role, send: Callable, *args, **kwargs) -> None:
        users = await user_gateway.get_users_by_role(role)
        for user in users:
            try:
                await send(user.telegram_id, *args, **kwargs)
            except TelegramForbiddenError:
                pass
            except Exception:
                logger.exception("Failed to notify", tg_id=user.id, role=role.name)


notification_service = NotificationService()
