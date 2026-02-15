from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from app.core.constants.dirs import SETTINGS
from app.dialogs import SendAction
from app.dialogs.rows.common import BackCallback
from app.dialogs.send.admin.settings import send_settings_menu

router = Router()

DIR = SETTINGS


@router.message(Command(DIR))
async def cmd_handler(message: Message):
    await send_settings_menu(message, SendAction.ANSWER)


@router.callback_query(BackCallback.filter(F.dir == DIR))
async def cb_back_handler(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    await send_settings_menu(
        callback.message, SendAction.EDIT  # pyright: ignore[reportArgumentType]
    )
