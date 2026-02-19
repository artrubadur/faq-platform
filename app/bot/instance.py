from aiogram import Bot, Dispatcher
from redis.asyncio import Redis

from app.bot.storage import LSTStorage
from app.core.config import config

redis_client = Redis(host=config.redis_host, password=config.redis_pass)

storage = LSTStorage(redis_client, config.redis_long_ttl, config.redis_short_ttl)

bot = Bot(config.tg_bot_token)
dp = Dispatcher(storage=storage)
