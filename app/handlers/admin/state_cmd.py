from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.dialogs.actions import SendAction
from app.dialogs.send.admin.state import send_state
from app.utils.data.temp import cleanup_temp_data

router = Router()


@router.message(Command("state"))
async def cmd_handler(message: Message, state: FSMContext, command: CommandObject):
    args = command.args
    if args == "clear":
        await state.set_state(None)
        await cleanup_temp_data(state)

    data = await state.get_data()

    await send_state(message, SendAction.ANSWER, data)
