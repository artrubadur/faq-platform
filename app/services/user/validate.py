import re

from app.storage.db.models.user import Role


def validate_id(tg_id: str | int) -> int:
    if isinstance(tg_id, int):
        return tg_id

    if tg_id.isdigit():
        return int(tg_id)

    raise ValueError("ID is incorrect")


def validate_username(username: str | None) -> str | None:
    if username is None:
        return None

    res_val = username.removeprefix("@")

    if len(username) < 4:
        raise ValueError("The username is too short")

    if len(username) > 32:
        raise ValueError("The username is too long")

    if not bool(re.match(r"^[a-zA-Z0-9_]+$", username)):
        raise ValueError("The username has unexcepted symbols")

    return res_val


def validate_role(role: str) -> str:
    res_val = role.lower()

    if res_val not in Role:
        raise ValueError("An unexpected role")

    return res_val
