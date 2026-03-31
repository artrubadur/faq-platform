import asyncio

from loguru import logger

from app.bot.handlers import admin_router, common_router, public_router
from app.bot.instance import bot, dp, redis_client
from app.bot.middlewares import (
    AdminMiddleware,
    BannedMiddleware,
    LastMessageMiddleware,
    LogHandlerMiddleware,
    RateLimitMiddleware,
)
from app.core import commands_status, constants_status, messages_status, requests_status
from app.core.config import config
from app.core.logging.setup import setup_logging
from app.services.user.admin_sync import sync_admin_roles
from app.storage.core import close_db, init_db


async def startup():
    setup_logging(config.paths.logging)
    await init_db()
    await sync_admin_roles(config.bot.admins)

    logger.info(messages_status)
    logger.info(constants_status)
    logger.info(commands_status)
    logger.info(requests_status)

    banned_mw = BannedMiddleware()
    dp.message.middleware(banned_mw)
    dp.callback_query.middleware(banned_mw)

    if config.rate_limit.enabled:
        rate_limit_mw = RateLimitMiddleware(
            redis=redis_client,
            max_requests=config.rate_limit.max_requests,
            window=config.rate_limit.window,
            skip_admin=config.rate_limit.skip_admin,
        )
        dp.message.middleware(rate_limit_mw)
        dp.callback_query.middleware(rate_limit_mw)

    last_message_mw = LastMessageMiddleware(bot)
    dp.message.middleware(last_message_mw)
    dp.callback_query.middleware(last_message_mw)

    log_handler_mw = LogHandlerMiddleware()
    dp.message.middleware(log_handler_mw)
    dp.callback_query.middleware(log_handler_mw)

    admin_mw = AdminMiddleware()
    admin_router.message.middleware(admin_mw)
    admin_router.callback_query.middleware(admin_mw)

    dp.include_router(admin_router)
    dp.include_router(common_router)
    dp.include_router(public_router)

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
