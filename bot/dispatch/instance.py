from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from redis.asyncio import Redis

from bot.core.config import config
from bot.utils.state.temp import TempStorage

redis_client = Redis(host=config.redis.host, password=config.redis.password)

storage = TempStorage(redis_client, config.redis.long_ttl, config.redis.short_ttl)

bot_session = AiohttpSession(proxy=config.bot.proxy)
bot = Bot(config.bot.token, session=bot_session)
dp = Dispatcher(storage=storage)
