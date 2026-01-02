from aiogram import Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.dialogs.actions import SendAction
from app.dialogs.rows.common import CloseCallback
from app.dialogs.send.root import (
    send_confirm_goto,
    send_invalid_path,
    send_start,
    send_state,
)
from app.utils.data.temp import cleanup_temp_data

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    full_name = message.from_user.full_name
    await send_start(message, SendAction.REPLY_DOCUMENT, full_name)


@router.callback_query(CloseCallback.filter())
async def cb_close_handler(callback: CallbackQuery):
    await callback.answer()
    await callback.message.delete()


@router.message(Command("goto"))
async def cmd_goto(message: Message, command: CommandObject):
    input_path = command.args
    if input_path is None:
        await send_invalid_path(message, SendAction.ANSWER, "The path is not set")
        return

    await send_confirm_goto(message, SendAction.ANSWER, input_path)


@router.message(Command("state"))
async def cmd_state(message: Message, state: FSMContext, command: CommandObject):
    args = command.args
    if args == "clear":
        await state.set_state(None)
        await cleanup_temp_data(state)

    data = await state.get_data()

    await send_state(message, SendAction.ANSWER, data)
