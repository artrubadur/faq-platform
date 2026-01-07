from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from app.dialogs.actions import SendAction
from app.dialogs.send.admin.goto import send_confirm_goto, send_invalid_path

router = Router()


@router.message(Command("goto"))
async def cmd_handler(message: Message, command: CommandObject):
    input_path = command.args
    if input_path is None:
        await send_invalid_path(message, SendAction.ANSWER, "The path is not set")
        return

    await send_confirm_goto(message, SendAction.ANSWER, input_path)
