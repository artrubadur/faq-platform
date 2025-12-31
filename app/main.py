import asyncio

from app.bot.instance import bot, dp
from app.bot.middleware import LastMessageMiddleware
from app.handlers import router
from app.storage.db.init import init_db


async def main():
    await init_db()

    last_msg_mw = LastMessageMiddleware(bot)
    dp.message.middleware(last_msg_mw)
    dp.callback_query.middleware(last_msg_mw)

    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped by user")
