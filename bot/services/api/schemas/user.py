from dataclasses import dataclass
from enum import StrEnum


class Role(StrEnum):
    BANNED = "banned"
    USER = "user"
    ADMIN = "admin"


@dataclass(slots=True, frozen=True)
class UserDto:
    id: int
    telegram_id: int
    username: str | None
    role: Role
