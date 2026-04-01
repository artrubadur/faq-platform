from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from bot.core.customization import messages

router = Router()


@router.message(Command("error"))
async def cmd_handler(message: Message, command: CommandObject):
    text = command.args or messages.format.fallback.exception
    raise Exception(text)
