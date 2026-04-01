from enum import StrEnum

from pydantic import BaseModel


class Role(StrEnum):
    BANNED = "banned"
    USER = "user"
    ADMIN = "admin"


class UserResponse(BaseModel):
    id: int
    telegram_id: int
    username: str | None
    role: Role


class UsersAmountResponse(BaseModel):
    amount: int
