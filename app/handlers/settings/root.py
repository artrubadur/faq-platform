from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import CallbackQuery, Message

from app.dialogs.rows.base import BackCallback

router = Router()
DIR = "settings"


@router.message(Command(DIR))
async def cmd_handler(message: Message, command: CommandObject):
    await message.answer("⚙ Settings")


@router.callback_query(BackCallback.filter(F.dir == DIR))
async def cb_back_handler(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    await callback.message.answer("👤 Settings")


@router.callback_query(F.data == "close")
async def cb_close_handler(callback: CallbackQuery):
    await callback.answer()
    await callback.message.delete()
