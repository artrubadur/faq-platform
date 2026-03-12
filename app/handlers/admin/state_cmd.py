from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from loguru import logger

from app.core.customization import messages
from app.dialogs.actions import SendAction
from app.dialogs.send.admin.misc import send_invalid_argument, send_json
from app.utils.state import clear_data, get_data, set_data, update_data

router = Router()


@router.message(Command("state"))
async def cmd_handler(
    message: Message,
    command: CommandObject,
    bot: Bot,
    dispatcher: Dispatcher,
):
    args = command.args.split() if command.args else []

    scope = "long" if "long" in args else "short"
    args = [a for a in args if a not in ("long", "short")]

    if not args:
        target_id = message.from_user.id
        data = await get_data(bot, dispatcher, target_id, scope)
        logger.debug("State obtained", id=target_id, scope=scope)
        return await send_json(message, SendAction.ANSWER, data)

    if args[0].isdigit():
        action = "get"
        target_id = int(args[0])
        remaining_args = args[1:]
    else:
        action = args[0].lower()
        if len(args) > 1 and args[1].isdigit():
            target_id = int(args[1])
            remaining_args = args[2:]
        else:
            target_id = message.from_user.id
            remaining_args = args[1:]

    match action:
        case "get":
            data = await get_data(bot, dispatcher, target_id, scope)
            logger.debug("State obtained", id=target_id, scope=scope)
            return await send_json(message, SendAction.ANSWER, data)
        case "clear":
            await clear_data(bot, dispatcher, target_id, scope)
            logger.debug("State cleared", id=target_id, scope=scope)
            return await send_json(message, SendAction.ANSWER, {})

    if not remaining_args:
        return await send_invalid_argument(
            message, SendAction.REPLY, messages.exceptions.misc.invalid_changes
        )

    kwargs = {}
    for pair in remaining_args:
        parts = pair.split("=", 1)
        if len(parts) != 2:
            return await send_invalid_argument(
                message, SendAction.REPLY, messages.exceptions.misc.invalid_changes
            )
        kwargs[parts[0]] = parts[1]

    match action:
        case "set":
            await set_data(bot, dispatcher, target_id, kwargs, scope)
            logger.debug("State set", id=target_id, scope=scope, data=kwargs)
            await send_json(message, SendAction.ANSWER, kwargs)
        case "update":
            data = await update_data(bot, dispatcher, target_id, kwargs, scope)
            await send_json(message, SendAction.ANSWER, data)
            logger.debug("State updated", id=target_id, scope=scope, data=kwargs)
        case _:
            await send_invalid_argument(
                message,
                SendAction.REPLY,
                action,
            )
