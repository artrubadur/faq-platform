from aiogram import Router
from aiogram.types import ErrorEvent
from loguru import logger

from app.core.exceptions import AppError
from app.dialogs.actions import SendAction
from app.dialogs.send.common import send_unexcepted_error, send_unhandled_exception
from app.services.notification import notify
from app.storage.models.user import Role

router = Router()


@router.errors()
async def errors_handler(event: ErrorEvent):
    exception = event.exception
    update = event.update
    message = update.message

    logger.exception(
        "Unexcepted error",
        tg_id=message.chat.id,
        username=message.chat.username,
        msg_id=message.message_id,
    )

    should_notify = (
        isinstance(exception, AppError)
        and exception.should_notify
        or not isinstance(exception, AppError)
    )

    if message is not None and should_notify:
        await send_unexcepted_error(message, SendAction.ANSWER)

    await notify(Role.ADMIN, send_unhandled_exception, exception)

    return True
