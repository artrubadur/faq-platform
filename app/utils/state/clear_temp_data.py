from aiogram import Bot, Dispatcher


async def clear_temp_data(user_id: int, bot: Bot, dispatcher: Dispatcher):
    context = dispatcher.fsm.get_context(bot, chat_id=user_id, user_id=user_id)
    data = await context.get_data()
    clean_data = {k: v for k, v in data.items() if not k.startswith("tmp_")}
    await context.set_data(clean_data)
    return clean_data
