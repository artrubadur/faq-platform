from aiogram.types import Message, MessageOriginUser

from bot.core.customization import messages
from bot.services.user.validate import validate_id, validate_role, validate_username
from bot.utils.format.input import format_input


def process_identity_msg(message: Message):
    if message.contact:
        input_id, input_username = message.contact.user_id, None
        if input_id is None:
            raise ValueError(messages.process.user.contact_invalid)
    elif isinstance(message.forward_origin, MessageOriginUser):
        input_id = message.forward_origin.sender_user.id
        input_username = message.forward_origin.sender_user.username
    elif message.forward_origin is not None:
        raise ValueError(messages.process.user.identity_invalid)
    elif message.text:
        input_id, input_username = format_input(message.text), None
    else:
        raise ValueError(messages.process.user.identity_invalid)

    valid_id = validate_id(input_id)
    return valid_id, input_username


def process_username_msg(message: Message):
    input_username = message.text
    if input_username is None:
        raise ValueError(messages.process.user.username_invalid)

    formatted_username = format_input(input_username)
    valid_username = validate_username(formatted_username)
    return valid_username


def process_role_msg(message: Message):
    input_role = message.text
    if input_role is None:
        raise ValueError(messages.process.user.role_invalid)

    input_role = format_input(input_role)
    valid_role = validate_role(input_role)
    return valid_role
