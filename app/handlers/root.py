from aiogram import Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import FSInputFile, Message, ReplyKeyboardRemove

from app.dialogs.send.root import send_confirm_goto, send_invalid_path
from app.utils.validate.root import validate_path

router = Router()


class Reg(StatesGroup):
    name = State()
    age = State()


photo = FSInputFile("C:\\Users\\Юля\\Downloads\\загружено.gif")


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.reply_document(
        document=photo,
        caption=f"You started the bot, {message.from_user.full_name}!",
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(Command("goto"))
async def cmd_goto(message: Message, command: CommandObject):
    input_path = command.args
    try:
        valid_path = validate_path(input_path)
    except ValueError as e:
        await send_invalid_path(message, exception=str(e))
        return

    await send_confirm_goto(message, valid_path)
