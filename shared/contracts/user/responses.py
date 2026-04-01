from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class Role(StrEnum):
    BANNED = "banned"
    USER = "user"
    ADMIN = "admin"


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    telegram_id: int
    username: str | None
    role: Role


class UsersAmountResponse(BaseModel):
    amount: int
