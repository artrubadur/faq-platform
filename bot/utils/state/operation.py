from typing import Any

from bot.utils.state.temp import TempContext


async def start_operation(state: TempContext, **kwargs):
    await state.set_data({"in_operation": True, **kwargs})


async def extend_operation(state: TempContext):
    await state.update_data(in_operation=True)


def is_operation_expired(state_data: dict[str, Any]) -> bool:
    return not state_data.get("in_operation", False)
