from aiogram import Bot, Dispatcher


async def update_data(user_id: int, bot: Bot, dispatcher: Dispatcher, **changes):
    context = dispatcher.fsm.get_context(bot, chat_id=user_id, user_id=user_id)
    await context.update_data(**changes)
    return await context.get_data()
