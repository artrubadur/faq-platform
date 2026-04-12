from bot.core.customization import messages
from shared.contracts.types import INT64_MAX


def validate_int64_id(value: str | int, error_message: str) -> int:
    if isinstance(value, int):
        int_value = value
    elif value.isdigit():
        int_value = int(value)
    else:
        raise ValueError(error_message)

    if int_value < 1 or int_value > INT64_MAX:
        raise ValueError(error_message)

    return int_value


def validate_page(page: str):
    try:
        int_page = int(page)
    except ValueError:
        raise ValueError(messages.validation.common.page_invalid)

    if int_page == 0:
        raise ValueError(messages.validation.common.page_invalid)

    return int_page


def resolve_page(page: int, max_page: int) -> int:
    if max_page <= 0:
        return 0

    resolved_page = page
    if page < 0:
        resolved_page = max_page + page + 1

    if resolved_page < 1:
        return 1

    return min(max_page, resolved_page)
