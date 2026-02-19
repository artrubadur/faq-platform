from aiogram import Bot, Dispatcher
from redis.asyncio import Redis
from aiogram.fsm.storage.redis import RedisStorage

from app.core.config import config

redis_client = Redis(
    host=config.redis_host,
    password=config.redis_pass
)
storage = RedisStorage(
    redis_client,
    state_ttl=config.redis_ttl,
    data_ttl=config.redis_ttl
)

bot = Bot(config.tg_bot_token)
dp = Dispatcher()
