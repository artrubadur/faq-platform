from aiogram import F, Router
from aiogram.types import CallbackQuery

import app.dialogs.markups.user as mu
from app.core.constants.emoji import EmojiNav
from app.dialogs.rows.base import BackCallback, CancelCallback

router = Router()
DIR = "settings.users"


@router.callback_query(F.data == DIR)
async def cb_handler(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text("👤 User Management", reply_markup=mu.main)


@router.callback_query(BackCallback.filter(F.dir == DIR))
async def cb_back_handler(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    await callback.message.answer("👤 User Management", reply_markup=mu.main)


@router.callback_query(CancelCallback.filter(F.dir == DIR))
async def cb_cancel_handler(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.edit_text(
        f"{callback.message.html_text}\n{EmojiNav.CANCEL} CANCELED {EmojiNav.CANCEL}",
        parse_mode="HTML",
    )

    await callback.message.answer("👤 User Management", reply_markup=mu.main)
