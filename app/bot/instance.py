from aiogram import Bot, Dispatcher
from redis.asyncio import Redis

from app.core.config import config
from app.storage.temp import TempStorage

redis_client = Redis(host=config.redis_host, password=config.redis_pass)

storage = TempStorage(redis_client, config.redis_long_ttl, config.redis_short_ttl)

bot = Bot(config.tg_token)
dp = Dispatcher(storage=storage)
