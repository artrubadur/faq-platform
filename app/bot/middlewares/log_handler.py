from aiogram import BaseMiddleware
from loguru import logger


class LogHandlerMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user_id = event.from_user.id

        handler_obj = data.get("handler")
        if handler_obj:
            module = handler_obj.callback.__module__
            func_name = handler_obj.callback.__name__
            full_path = f"{module}.{func_name}"
        else:
            full_path = "unknown"

        logger.debug("Start handler for user", handler=full_path, tg_id=user_id)

        result = await handler(event, data)
        logger.debug("Handler finished successfully", handler=full_path)
        return result
