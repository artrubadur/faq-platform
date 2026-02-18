from aiogram.types import Message

from app.core.messages import messages
from app.services.user.validate import validate_id, validate_role, validate_username
from app.utils.format.input import format_input


async def process_identity_msg(message: Message):
    if message.contact:
        input_id, input_username = message.contact.user_id, None
        if input_id is None:
            raise ValueError(messages.process.user.contact_invalid)
    elif message.forward_from:
        input_id, input_username = (
            message.forward_from.id,
            message.forward_from.username,
        )
    elif message.text:
        input_id, input_username = format_input(message.text), None
    else:
        raise ValueError(messages.process.user.identity_invalid)

    valid_id = validate_id(input_id)
    return valid_id, input_username


async def process_username_msg(message: Message):
    input_username = message.text
    if input_username is None:
        raise ValueError(messages.process.user.username_invalid)

    formatted_username = format_input(input_username)
    valid_username = validate_username(formatted_username)
    return valid_username


async def process_role_msg(message: Message):
    input_role = message.text
    if input_role is None:
        raise ValueError(messages.process.user.role_invalid)

    input_role = format_input(input_role)
    valid_role = validate_role(input_role)
    return valid_role
