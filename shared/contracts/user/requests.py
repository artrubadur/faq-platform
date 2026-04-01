from typing import Literal

from pydantic import BaseModel, Field, model_validator

from shared.contracts.user.responses import Role

UserFields = Literal["id", "telegram_id", "username", "role"]


class CreateUserRequest(BaseModel):
    id: int
    username: str | None
    role: Role

    @model_validator(mode="after")
    def validate_role(self) -> "CreateUserRequest":
        if self.role == Role.ADMIN:
            raise ValueError("Admin user cannot be created")
        return self


class UpdateUserRequest(BaseModel):
    username: str | None = None
    role: Role | None = None

    @model_validator(mode="after")
    def validate_role(self) -> "UpdateUserRequest":
        if self.role is None:
            raise ValueError("Role cannot be null")
        if self.role == Role.ADMIN:
            raise ValueError("Admin user cannot be updated")
        return self


class ListUsersRequest(BaseModel):
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
    order_by: UserFields
    ascending: bool


class UsersByRoleRequest(BaseModel):
    role: Role
