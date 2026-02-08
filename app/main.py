import asyncio
from pathlib import Path

from loguru import logger

from app.bot.instance import bot, dp
from app.bot.middlewares import LastMessageMiddleware, LogHandlerMiddleware
from app.core.config import config
from app.core.logging import setup_logging
from app.handlers import router
from app.storage.init import init_db

CONFIG_DIR = Path.cwd() / "config"


async def main():
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


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
