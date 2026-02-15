from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from app.core.responses import responses
from app.dialogs import SendAction
from app.dialogs.send.public.commands import send_command

router = Router()

if len(responses.commands) > 0:

    @router.message(Command(commands=list(responses.commands.keys())))
    async def dynamic_cmd_handler(message: Message, command: CommandObject):
        text = responses.commands[command.command]
        await send_command(message, SendAction.ANSWER, message, text)
