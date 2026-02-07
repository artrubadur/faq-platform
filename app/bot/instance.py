from aiogram import Bot, Dispatcher

from app.core.config import config

bot = Bot(config.tg_bot_token)
dp = Dispatcher()
