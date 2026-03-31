from aiogram import BaseMiddleware, Bot

from app.utils.state.history import LastMessage, last_message_var


class LastMessageMiddleware(BaseMiddleware):
    def __init__(self, bot: Bot):
        self.bot = bot

    async def __call__(self, handler, event, data):
        last_message = LastMessage(self.bot)
        token = last_message_var.set(last_message)
        data["last_message"] = last_message

        try:
            return await handler(event, data)
        finally:
            last_message_var.reset(token)
