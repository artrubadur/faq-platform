from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

router = Router()


@router.message(Command("error"))
async def cmd_error(message: Message, command: CommandObject):
    text = command.args or "Fake exception"
    raise RuntimeError(text)
