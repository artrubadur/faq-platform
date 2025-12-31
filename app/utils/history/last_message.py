from contextvars import ContextVar

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, Message


class LastMessage:
    def __init__(self, bot: Bot):
        self.bot = bot

    async def set(self, message: Message, state: FSMContext):
        await state.update_data(glb_last_bot_message_id=message.message_id)

    async def get_id(self, state: FSMContext) -> int | None:
        data = await state.get_data()
        return data.get("glb_last_bot_message_id", None)

    async def edit_reply_markup(
        self,
        message: Message,
        state: FSMContext,
        reply_markup: InlineKeyboardMarkup | None = None,
    ) -> bool:
        message_id = await self.get_id(state)

        if message_id is None:
            return False

        try:
            await self.bot.edit_message_reply_markup(
                chat_id=message.chat.id,
                message_id=message_id,
                reply_markup=reply_markup,
            )
            return True
        except Exception:
            return False

    async def delete(
        self,
        message: Message,
        state: FSMContext,
    ) -> bool:
        message_id = await self.get_id(state)

        if message_id is None:
            return False

        try:
            await self.bot.delete_message(
                chat_id=message.chat.id, message_id=message_id
            )
            return True
        except Exception:
            return False


last_message_var: ContextVar[LastMessage | None] = ContextVar(
    "last_message", default=None
)
