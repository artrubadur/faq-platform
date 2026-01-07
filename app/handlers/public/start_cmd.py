from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.dialogs.actions import SendAction
from app.dialogs.send.public.start import send_start

router = Router()


@router.message(CommandStart())
async def cmd_handler(message: Message):
    full_name = message.from_user.full_name
    await send_start(message, SendAction.ANSWER, full_name)
