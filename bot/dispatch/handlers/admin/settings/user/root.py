from aiogram import F, Router
from aiogram.types import CallbackQuery

from bot.core.customization import messages
from bot.core.dirs import USERS
from bot.dialogs import SendAction
from bot.dialogs.rows.common import BackCallback, CancelCallback
from bot.dialogs.send.admin.settings import send_users_menu
from bot.utils.state.temp import TempContext

router = Router()

DIR = USERS[1]


@router.callback_query(F.data == DIR)
async def user_cb_handler(callback: CallbackQuery):
    await callback.answer()
    await send_users_menu(
        callback.message, SendAction.EDIT  # pyright: ignore[reportArgumentType]
    )


@router.callback_query(BackCallback.filter(F.dir == DIR))
async def user_back_cb_handler(callback: CallbackQuery, state: TempContext):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    await state.clear()

    await send_users_menu(
        callback.message, SendAction.ANSWER  # pyright: ignore[reportArgumentType]
    )


@router.callback_query(CancelCallback.filter(F.dir == DIR))
async def user_cancel_cb_handler(callback: CallbackQuery, state: TempContext):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.edit_text(
        messages.format.canceled.format(old=callback.message.html_text),
        parse_mode="HTML",
    )

    await state.clear()

    await send_users_menu(
        callback.message, SendAction.ANSWER  # pyright: ignore[reportArgumentType]
    )
