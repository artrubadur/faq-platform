import traceback

from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import ErrorEvent

from app.dialogs.actions import SendAction
from app.dialogs.send.common import send_unexcepted_error, send_unhandled_exception
from app.repositories.users import UsersRepository
from app.services.user.service import UsersService
from app.storage.engine import async_session
from app.storage.models.user import Role
from app.utils.format.output import format_message

router = Router()


@router.errors()
async def errors_handler(event: ErrorEvent):
    exception = event.exception
    update = event.update

    message = update.message

    if message is not None:
        await send_unexcepted_error(message, SendAction.ANSWER)

    message_str = None if message is None else format_message(message)
    tb_string = traceback.format_exc()
    print(
        f"Unhandled error: {exception}\nMessage:\n{message_str}\nTraceback:\n{tb_string}"
    )

    try:
        async with async_session() as session:
            repo = UsersRepository(session)
            service = UsersService(repo)
            try:
                users = await service.get_users_by_role(Role.ADMIN)
                for user in users:
                    await send_unhandled_exception(
                        user.telegram_id, exception  # pyright: ignore[reportArgumentType]
                    )
            except Exception as notification_exception:
                print(f"Failed to notify admins: {notification_exception}")

    except TelegramBadRequest:
        pass

    return True
