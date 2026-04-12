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
    if not page.isdigit():
        raise ValueError(messages.validation.common.page_invalid)
    int_page = int(page)

    if int_page < 1:
        raise ValueError(messages.validation.common.page_negative)

    return int_page
