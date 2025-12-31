from aiogram.fsm.context import FSMContext


async def cleanup_temp_data(state: FSMContext):
    data = await state.get_data()
    clean_data = {k: v for k, v in data.items() if not k.startswith("tmp_")}
    await state.set_data(clean_data)
