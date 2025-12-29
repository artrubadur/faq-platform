from aiogram import Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import CallbackQuery, Message

from app.dialogs.actions import SendAction
from app.dialogs.rows.base import CloseCallback
from app.dialogs.send.root import send_confirm_goto, send_invalid_path, send_start
from app.utils.validate.root import validate_path

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await send_start(message, action=SendAction.REPLY_DOCUMENT)


@router.message(Command("goto"))
async def cmd_goto(message: Message, command: CommandObject):
    input_path = command.args
    try:
        valid_path = validate_path(input_path)
    except ValueError as e:
        await send_invalid_path(message, exception=str(e), action=SendAction.ANSWER)
        return

    await send_confirm_goto(message, valid_path, action=SendAction.ANSWER)


@router.callback_query(CloseCallback.filter())
async def cb_close_handler(callback: CallbackQuery):
    await callback.answer()
    await callback.message.delete()
