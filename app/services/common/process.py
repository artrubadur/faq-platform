from aiogram.types import Message

from app.core.customization import messages
from app.services.common.validate import validate_page
from app.utils.format.input import format_input


def process_page_msg(message: Message) -> int:
    input_page = message.text
    if input_page is None:
        raise ValueError(messages.process.common.page_invalid)

    formatted_page = format_input(input_page)
    valid_page = validate_page(formatted_page)
    return valid_page
