from aiogram import Bot, Dispatcher


async def get_data(user_id: int, bot: Bot, dispatcher: Dispatcher):
    context = dispatcher.fsm.get_context(bot, chat_id=user_id, user_id=user_id)
    return await context.get_data()
