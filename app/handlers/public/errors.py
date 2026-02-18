from aiogram import Router
from aiogram.types import ErrorEvent
from loguru import logger

from app.core.exceptions import AppError
from app.dialogs.actions import SendAction
from app.dialogs.send.common import send_unexcepted_error

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

    should_notify = (
        isinstance(exception, AppError)
        and exception.should_notify
        or not isinstance(exception, AppError)
    )

    if message is not None and should_notify:
        await send_unexcepted_error(message, SendAction.ANSWER, message)

    return True
