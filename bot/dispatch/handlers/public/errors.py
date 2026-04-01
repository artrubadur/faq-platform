from aiogram import Router
from aiogram.types import ErrorEvent
from loguru import logger

from bot.dialogs.actions import SendAction
from bot.dialogs.send.common import send_unexcepted_error
from bot.services.api.exceptions import InternalApiError

router = Router()


@router.errors()
async def errors_handler(event: ErrorEvent):
    exception = event.exception
    update = event.update
    message = update.message

    extra = (
        {}
        if message is None
        else {
            "tg_id": message.chat.id,
            "username": message.chat.username,
            "msg_id": message.message_id,
        }
    )
    logger.exception("Unexcepted error", extra)

    if message is not None and isinstance(exception, InternalApiError):
        await send_unexcepted_error(message, SendAction.ANSWER, message)

    return True
