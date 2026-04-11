from typing import Any

from bot.services.http_client import orchestrator_client
from shared.api.client import ApiClient
from shared.contracts.user.requests import (
    CreateUserRequest,
    ListUsersRequest,
    UpdateUserRequest,
    UserFields,
    UsersByRoleRequest,
)
from shared.contracts.user.responses import Role, UserResponse, UsersAmountResponse

_UNSET = object()


class UserGateway:
    def __init__(
        self,
        client: ApiClient,
    ) -> None:
        self.client = client

    async def create_user(
        self,
        id: int,
        username: str | None,
        role: Role,
    ) -> UserResponse:
        request = CreateUserRequest(
            id=id,
            username=username,
            role=role,
        )
        data = await self.client.post(
            "/users",
            json_data=request.model_dump(mode="json"),
        )
        return UserResponse.model_validate(data)

    async def get_user(self, id: int) -> UserResponse:
        data = await self.client.get(f"/users/{id}")
        return UserResponse.model_validate(data)

    async def get_user_amount(self) -> int:
        data = await self.client.get("/users/count")
        return UsersAmountResponse.model_validate(data).amount

    async def get_paginated_users(
        self,
        page: int,
        page_size: int,
        order_by: UserFields,
        ascending: bool,
    ) -> list[UserResponse]:
        request = ListUsersRequest(
            page=page,
            page_size=page_size,
            order_by=order_by,
            ascending=ascending,
        )
        data = await self.client.get(
            "/users",
            params=request.model_dump(mode="json"),
        )
        return [UserResponse.model_validate(item) for item in data]

    async def get_users_by_role(self, role: Role) -> list[UserResponse]:
        request = UsersByRoleRequest(role=role)
        data = await self.client.get(
            "/users/by-role",
            params=request.model_dump(mode="json"),
        )
        return [UserResponse.model_validate(item) for item in data]

    async def delete_user(self, id: int) -> UserResponse:
        data = await self.client.delete(f"/users/{id}")
        return UserResponse.model_validate(data)

    async def update_user(
        self,
        id: int,
        role: Role,
        username: str | None | object = _UNSET,
    ) -> UserResponse:
        request_data: dict[str, Any] = {"role": role}
        if username is not _UNSET:
            request_data["username"] = username

        request = UpdateUserRequest(**request_data)
        data = await self.client.patch(
            f"/users/{id}",
            json_data=request.model_dump(mode="json", exclude_unset=True),
        )
        return UserResponse.model_validate(data)


user_gateway = UserGateway(orchestrator_client)
