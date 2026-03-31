from aiogram import Router
from aiogram.types import CallbackQuery, Message

from app.dialogs.actions import SendAction
from app.dialogs.rows.common import CloseCallback
from app.dialogs.send.common import send_banned, send_rate_limit

router = Router()


@router.callback_query(CloseCallback.filter())
async def cb_close_handler(callback: CallbackQuery):
    await callback.answer()
    await callback.message.delete()


async def banned_handler(event: Message | CallbackQuery):
    if isinstance(event, Message):
        await send_banned(event, SendAction.ANSWER, event)
        return

    if event.message is not None:
        await event.answer()
        await send_banned(
            event.message,  # pyright: ignore[reportArgumentType]
            SendAction.ANSWER,
            event.message,  # pyright: ignore[reportArgumentType]
        )


async def rate_limit_handler(event: Message | CallbackQuery):
    if isinstance(event, Message):
        await send_rate_limit(event, SendAction.ANSWER, event)
        return

    if event.message is not None:
        await event.answer()
        await send_rate_limit(
            event.message,  # pyright: ignore[reportArgumentType]
            SendAction.ANSWER,
            event.message,  # pyright: ignore[reportArgumentType]
        )
