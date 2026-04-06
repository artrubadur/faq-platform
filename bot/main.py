from loguru import logger

from bot.core.config import config
from bot.core.customization.commands import status as commands_status
from bot.core.customization.constants import status as constants_status
from bot.core.customization.messages import status as messages_status
from bot.dispatch.handlers import admin_router, common_router, public_router
from bot.dispatch.instance import bot, dp, redis_client
from bot.dispatch.middlewares import (
    AdminMiddleware,
    BannedMiddleware,
    LastMessageMiddleware,
    LogHandlerMiddleware,
    RateLimitMiddleware,
)
from bot.services.http_client import close_orchestrator_client


async def startup():
    logger.info(messages_status)
    logger.info(constants_status)
    logger.info(commands_status)

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
    await close_orchestrator_client()
