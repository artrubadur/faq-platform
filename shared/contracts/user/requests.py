from pydantic import BaseModel

from shared.contracts.user.responses import Role


class CreateUserRequest(BaseModel):
    id: int
    username: str | None
    role: Role


class UpdateUserRequest(BaseModel):
    username: str | None = None
    role: Role | None = None


class ListUsersRequest(BaseModel):
    page: int
    page_size: int
    order_by: str
    ascending: bool


class UsersByRoleRequest(BaseModel):
    role: Role
