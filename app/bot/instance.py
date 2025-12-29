from aiogram import Bot, Dispatcher

from app.core.config import API_TOKEN

bot = Bot(token=API_TOKEN)  # pyright: ignore[reportArgumentType]
dp = Dispatcher()
