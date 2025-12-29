# pyright: reportArgumentType=false
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from app.dialogs import SendAction
from app.dialogs.rows.base import BackCallback
from app.dialogs.send.settings import send_settings_menu

router = Router()
DIR = "settings"


@router.message(Command(DIR))
async def cmd_handler(message: Message):
    await send_settings_menu(message, action=SendAction.ANSWER)


@router.callback_query(BackCallback.filter(F.dir == DIR))
async def cb_back_handler(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    await send_settings_menu(callback.message, action=SendAction.EDIT)
