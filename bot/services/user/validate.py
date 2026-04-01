import re

from bot.core.customization import messages
from shared.contracts.user.responses import Role


def validate_id(id: str | int) -> int:
    if isinstance(id, int):
        return id

    if id.isdigit():
        return int(id)

    raise ValueError(messages.validation.user.id_invalid)


def validate_username(username: str | None) -> str | None:
    if username is None:
        return None

    res_val = username.removeprefix("@")

    if len(username) <= 4:
        raise ValueError(messages.validation.user.username_short)

    if len(username) > 32:
        raise ValueError(messages.validation.user.username_long)

    if not bool(re.match(r"^[a-zA-Z0-9_]+$", username)):
        raise ValueError(messages.validation.user.username_unexcepted_symbols)

    return res_val


def validate_role(role: str) -> Role:
    try:
        role_enum = Role(role.lower())
    except ValueError as exc:
        raise ValueError(messages.validation.user.role_unexcepted) from exc

    return role_enum
