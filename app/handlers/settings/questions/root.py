# pyright: reportArgumentType=false
from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.core.constants.emoji import EmojiNav
from app.dialogs import SendAction
from app.dialogs.rows.base import BackCallback, CancelCallback
from app.dialogs.send.settings import send_questions_menu

router = Router()
DIR = "settings.questions"


@router.callback_query(F.data == DIR)
async def question_cb_handler(callback: CallbackQuery):
    await callback.answer()
    await send_questions_menu(callback.message, action=SendAction.EDIT)


@router.callback_query(BackCallback.filter(F.dir == DIR))
async def question_back_cb_handler(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    await send_questions_menu(callback.message, action=SendAction.ANSWER)


@router.callback_query(CancelCallback.filter(F.dir == DIR))
async def question_cancel_cb_handler(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.edit_text(
        f"{callback.message.html_text}\n{EmojiNav.CANCEL} CANCELED {EmojiNav.CANCEL}",
        parse_mode="HTML",
    )

    await send_questions_menu(callback.message, action=SendAction.ANSWER)
