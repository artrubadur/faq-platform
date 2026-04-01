from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from bot.core.customization.commands import commands
from bot.dialogs import SendAction
from bot.dialogs.send.public.commands import send_command

router = Router()

if len(commands.commands) > 0:

    @router.message(Command(commands=list(commands.commands.keys())))
    async def dynamic_cmd_handler(message: Message, command: CommandObject):
        text = commands.commands[command.command]
        await send_command(message, SendAction.ANSWER, message, text)
