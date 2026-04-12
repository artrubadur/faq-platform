from typing import Literal

from pydantic import BaseModel, Field

from shared.contracts.types import Int64Id
from shared.contracts.user.responses import Role

UserFields = Literal["id", "telegram_id", "username", "role"]


class CreateUserRequest(BaseModel):
    id: Int64Id
    username: str | None
    role: Role


class UpdateUserRequest(BaseModel):
    username: str | None = None
    role: Role | None = None


class ListUsersRequest(BaseModel):
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
    order_by: UserFields
    ascending: bool


class UsersByRoleRequest(BaseModel):
    role: Role
