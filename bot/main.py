import asyncio

from aiogram.methods import DeleteWebhook
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
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


def configure_pipeline() -> None:
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

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)


async def on_startup() -> None:
    if config.bot.mode == "webhook":
        await bot.set_webhook(
            url=config.bot.webhook.url,
            secret_token=config.bot.webhook.secret_token,
            drop_pending_updates=config.bot.webhook.drop_pending_updates,
        )
        logger.info(f"Webhook configured at {config.bot.webhook.url}")
        return

    await bot(
        DeleteWebhook(drop_pending_updates=config.bot.webhook.drop_pending_updates)
    )


async def on_shutdown() -> None:
    if config.bot.mode == "webhook":
        await bot(DeleteWebhook())

    await close_orchestrator_client()
    logger.info("Bot stopped")


async def run_polling() -> None:
    logger.info("Starting bot in polling mode")
    await dp.start_polling(bot)


def run_webhook() -> None:
    logger.info(
        f"Starting bot in webhook mode at 0.0.0.0:8080{config.bot.webhook.path}",
    )
    app = web.Application()

    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=config.bot.webhook.secret_token,
    )
    webhook_requests_handler.register(app, path=config.bot.webhook.path)
    setup_application(app, dp, bot=bot)

    web.run_app(
        app,
        host="0.0.0.0",
        port=8080,
        print=None,
    )


def run() -> None:
    configure_pipeline()

    if config.bot.mode == "webhook":
        run_webhook()
        return

    asyncio.run(run_polling())
