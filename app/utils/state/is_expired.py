from typing import Any


def is_expired(state_data: dict[str, Any]) -> bool:
    return state_data.get("tmp_in_operation", False) != True