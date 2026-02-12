import asyncio
import signal
from pathlib import Path

from loguru import logger

from app.bot.instance import bot, dp
from app.bot.middlewares import LastMessageMiddleware, LogHandlerMiddleware
from app.core.config import config
from app.core.logging.setup import setup_logging
from app.handlers import router
from app.storage.core import close_db, init_db

CONFIG_DIR = Path.cwd() / "config"


async def ignore_signals():
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, signal.SIG_IGN)
    await asyncio.Event().wait()


async def startup():
    setup_logging(CONFIG_DIR / f"logging.{config.env}.yml")
    await init_db()

    last_message_mw = LastMessageMiddleware(bot)
    dp.message.middleware(last_message_mw)
    dp.callback_query.middleware(last_message_mw)

    log_handler_mw = LogHandlerMiddleware()
    dp.message.middleware(log_handler_mw)
    dp.callback_query.middleware(log_handler_mw)

    dp.include_router(router)
    logger.info("Bot is starting")
    await dp.start_polling(bot)


@dp.shutdown()
async def shutdown():
    logger.info("Bot stopped by user")
    await close_db()


if __name__ == "__main__":
    try:
        asyncio.run(startup())
    except KeyboardInterrupt:
        pass
