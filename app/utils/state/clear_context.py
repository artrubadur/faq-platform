from aiogram import Bot, Dispatcher


async def clear_context(user_id: int, bot: Bot, dispatcher: Dispatcher, **data):
    context = dispatcher.fsm.get_context(bot, chat_id=user_id, user_id=user_id)
    await context.set_state(None)
    await context.set_data({})
    return {}
