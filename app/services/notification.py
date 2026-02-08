from typing import Callable

from aiogram.exceptions import TelegramForbiddenError
from loguru import logger

from app.repositories.users import UsersRepository
from app.services.user.service import UsersService
from app.storage.engine import async_session
from app.storage.models.user import Role


async def notify(role: Role, send: Callable, *args, **kwargs):
    async with async_session() as session:
        repo = UsersRepository(session)
        service = UsersService(repo)
        users = await service.get_users_by_role(role)
        for user in users:
            try:
                await send(user.telegram_id, *args, **kwargs)
            except TelegramForbiddenError:
                pass
            except Exception:
                logger.warning("Failed to notify", tg_id=user.id, role=role)
