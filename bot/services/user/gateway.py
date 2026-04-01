from bot.services.api.client import InternalApiClient, client
from bot.services.api.schemas.user import UserDto


class UserGateway:
    def __init__(
        self,
        client: InternalApiClient,
    ) -> None:
        self.client = client

    async def create_user(
        self,
        id: int,
        username: str | None,
        role: str,
    ) -> UserDto:
        data = await self.client.post(
            "/users",
            json_data={
                "id": id,
                "username": username,
                "role": role,
            },
        )
        return UserDto(**data)

    async def get_user(self, id: int) -> UserDto:
        data = await self.client.get(f"/users/{id}")
        return UserDto(**data)

    async def get_user_amount(self) -> int:
        data = await self.client.get("/users/count")
        return int(data["amount"])

    async def get_paginated_users(
        self,
        page: int,
        page_size: int,
        order_by: str,
        ascending: bool,
    ) -> list[UserDto]:
        data = await self.client.get(
            "/users",
            params={
                "page": page,
                "page_size": page_size,
                "order_by": order_by,
                "ascending": ascending,
            },
        )
        return [UserDto(**item) for item in data]

    async def get_users_by_role(self, role: str) -> list[UserDto]:
        data = await self.client.get(
            "/users/by-role",
            params={"role": role},
        )
        return [UserDto(**item) for item in data]

    async def delete_user(self, id: int) -> UserDto:
        data = await self.client.delete(f"/users/{id}")
        return UserDto(**data)

    async def update_user(self, id: int, **kwargs) -> UserDto:
        data = await self.client.put(
            f"/users/{id}",
            json_data=kwargs,
        )
        return UserDto(**data)


user_gateway = UserGateway(client)
