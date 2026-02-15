from aiogram import Bot, Dispatcher, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.core.constants.dirs import QUESTIONS
from app.core.constants.emojis import EmojiNav
from app.dialogs import SendAction
from app.dialogs.rows.common import BackCallback, CancelCallback
from app.dialogs.send.admin.settings import send_questions_menu
from app.utils.state import clear_context

router = Router()

DIR = QUESTIONS[1]


@router.callback_query(F.data == DIR)
async def question_cb_handler(callback: CallbackQuery):
    await callback.answer()
    await send_questions_menu(
        callback.message, SendAction.EDIT  # pyright: ignore[reportArgumentType]
    )


@router.callback_query(BackCallback.filter(F.dir == DIR))
async def question_back_cb_handler(
    callback: CallbackQuery, bot: Bot, dispatcher: Dispatcher
):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    await clear_context(callback.from_user.id, bot, dispatcher)

    await send_questions_menu(
        callback.message, SendAction.ANSWER  # pyright: ignore[reportArgumentType]
    )


@router.callback_query(CancelCallback.filter(F.dir == DIR))
async def question_cancel_cb_handler(
    callback: CallbackQuery, bot: Bot, dispatcher: Dispatcher
):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.edit_text(
        f"{callback.message.html_text}\n{EmojiNav.CANCEL} CANCELED {EmojiNav.CANCEL}",
        parse_mode="HTML",
    )

    await clear_context(callback.from_user.id, bot, dispatcher)

    await send_questions_menu(
        callback.message, SendAction.ANSWER  # pyright: ignore[reportArgumentType]
    )
