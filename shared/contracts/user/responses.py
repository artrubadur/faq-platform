from enum import StrEnum

from pydantic import BaseModel, ConfigDict

from shared.contracts.types import Int64Id


class Role(StrEnum):
    BANNED = "banned"
    USER = "user"
    ADMIN = "admin"


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Int64Id
    telegram_id: Int64Id
    username: str | None
    role: Role


class UsersAmountResponse(BaseModel):
    amount: int
