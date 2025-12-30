from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.bot.instance import bot


async def last_msg_save(message: Message, state: FSMContext):
    await state.update_data(last_bot_msg_id=message.message_id)


async def last_msg_remove_kb(message: Message, state: FSMContext):
    data = await state.get_data()
    msg_id = data.get("last_bot_msg_id")

    if msg_id:
        await bot.edit_message_reply_markup(
            chat_id=message.chat.id, message_id=msg_id, reply_markup=None
        )


async def last_msg_delete(message: Message, state: FSMContext):
    data = await state.get_data()
    msg_id = data.get("last_bot_msg_id")

    if msg_id:
        await bot.delete_message(
            chat_id=message.chat.id,
            message_id=msg_id,
        )
