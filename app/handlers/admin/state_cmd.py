from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from loguru import logger

from app.dialogs.actions import SendAction
from app.dialogs.send.admin.state import send_invalid_argument, send_state
from app.utils.state import clear_context, clear_temp_data, get_data, update_data

router = Router()


@router.message(Command("state"))
async def cmd_handler(
    message: Message,
    state: FSMContext,
    command: CommandObject,
    bot: Bot,
    dispatcher: Dispatcher,
):
    args = command.args.split() if command.args else []

    if not args:
        target_id = message.from_user.id

        data = await state.get_data()
        logger.debug("State obtained", id=target_id)
        return await send_state(message, SendAction.ANSWER, data)

    if args[0].isdigit():
        target_id = int(args[0])

        data = await get_data(target_id, bot, dispatcher)
        logger.debug("State obtained", id=target_id)
        return await send_state(message, SendAction.ANSWER, data)
    else:
        action = args[0].lower()

    match action:
        case "get":
            target_id = message.from_user.id

            remaining_args = args[1:]
            if remaining_args and remaining_args[0].isdigit():
                target_id = int(remaining_args[0])

            data = await get_data(target_id, bot, dispatcher)
            logger.debug("State obtained", id=target_id)
            await send_state(message, SendAction.ANSWER, data)

        case "clear":
            target_id = message.from_user.id
            mode = "-tmp"

            remaining_args = args[1:]
            if remaining_args and remaining_args[0].isdigit():
                target_id = int(remaining_args.pop(0))

            if "-all" in remaining_args:
                mode = "-all"

            match mode:
                case "-all":
                    data = await clear_context(target_id, bot, dispatcher)
                    logger.debug("State is cleared", id=target_id)
                    await send_state(message, SendAction.ANSWER, data)

                case "-tmp":
                    data = await clear_temp_data(target_id, bot, dispatcher)
                    logger.debug("Temporary state is cleared", id=target_id)
                    await send_state(message, SendAction.ANSWER, data)

        case "update":
            target_id = message.from_user.id

            remaining_args = args[1:]
            if remaining_args and remaining_args[0].isdigit():
                target_id = int(remaining_args.pop(0))

            if not remaining_args:
                return await send_invalid_argument(
                    message,
                    SendAction.REPLY,
                    "Pass changes with the `key=value` format",
                )

            changes = {}
            for kv_pair_str in remaining_args:
                kv_pair = kv_pair_str.split("=", 1)
                if len(kv_pair) != 2:
                    return await send_invalid_argument(
                        message,
                        SendAction.REPLY,
                        f"`{kv_pair_str}`. Use the `key=value` format",
                    )

                key, value = kv_pair
                changes[key] = value

            logger.debug("State updated", id=target_id, changes=changes)
            data = await update_data(target_id, bot, dispatcher, **changes)
            await send_state(message, SendAction.ANSWER, data)

        case _:
            await send_invalid_argument(message, SendAction.REPLY, f"`{action}`")
