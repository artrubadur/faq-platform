from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from loguru import logger
from sqlalchemy.exc import NoResultFound

from app.core.messages import messages
from app.dialogs.actions import SendAction
from app.dialogs.send.admin.misc import (
    send_banned,
    send_invalid_argument,
    send_unbanned,
)
from app.dialogs.send.common import send_access_denied
from app.repositories import UsersRepository
from app.services import UsersService
from app.storage.core import async_session
from app.storage.models.user import Role
from app.utils.state import update_data

router = Router()


async def _process_ban_handler(
    message: Message,
    command: CommandObject,
    bot: Bot,
    dispatcher: Dispatcher,
    role: Role,
):
    args = command.args
    if not args or not args.isdigit():
        await send_invalid_argument(
            message,
            SendAction.REPLY,
            "id",
        )
        return

    target_id = int(args)

    try:
        async with async_session() as session:
            repo = UsersRepository(session)
            service = UsersService(repo)
            updated = await service.update_user(
                target_id,
                role=role,
            )
    except NoResultFound:
        await send_invalid_argument(
            message,
            SendAction.REPLY,
            messages.exceptions.user.not_found.format(identity=target_id),
        )
        return
    except PermissionError as e:
        await send_access_denied(
            message,  # pyright: ignore[reportArgumentType]
            SendAction.REPLY,
            None,
            str(e),
        )
        return

    await update_data(
        bot,
        dispatcher,
        target_id,
        {"sender_role": role},
        "long",
    )

    return updated


@router.message(Command("ban"))
async def bun_cmd_handler(
    message: Message,
    command: CommandObject,
    bot: Bot,
    dispatcher: Dispatcher,
):
    updated = await _process_ban_handler(message, command, bot, dispatcher, Role.BANNED)
    if updated is None:
        return

    logger.debug("The user was banned", tg_id=message.from_user.id)

    await send_banned(
        message,
        SendAction.ANSWER,
        updated.telegram_id,
        updated.username,
    )


@router.message(Command("unban"))
async def unban_cmd_handler(
    message: Message,
    command: CommandObject,
    bot: Bot,
    dispatcher: Dispatcher,
):
    updated = await _process_ban_handler(message, command, bot, dispatcher, Role.USER)
    if updated is None:
        return

    logger.debug("The user was unbanned", tg_id=message.from_user.id)

    await send_unbanned(
        message,
        SendAction.ANSWER,
        updated.telegram_id,
        updated.username,
    )
