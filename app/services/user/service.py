from app.core.messages import messages
from app.repositories import UsersRepository
from app.storage.models.user import Role, User


class UsersService:
    def __init__(self, repository: UsersRepository):
        self.repository = repository

    async def create_user(self, id: int, username: str | None, role: str) -> User:
        return await self.repository.create(
            id,
            username,
            role,
        )

    async def get_user(self, id: int) -> User:
        return await self.repository.get_by_id(id)

    async def get_user_amount(self) -> int:
        return await self.repository.get_amount()

    async def get_paginated_users(
        self, page: int, page_size: int, order_by: str, ascending: bool
    ) -> list[User]:
        offset = (page - 1) * page_size
        users = await self.repository.get_slice(offset, page_size, order_by, ascending)
        return list(users)

    async def get_users_by_role(self, role: Role) -> list[User]:
        users = await self.repository.get_by_role(role)
        return list(users)

    async def delete_user(self, id: int) -> User:
        user = await self.repository.get_by_id(id)
        if user.role == Role.ADMIN:
            raise PermissionError(messages.responses.admin.user.deletion.access_denied)
        return await self.repository.delete(id)

    async def update_user(self, id: int, **kwargs) -> User:
        user = await self.repository.get_by_id(id)
        if user.role == Role.ADMIN:
            raise PermissionError(messages.responses.admin.user.update.access_denied)
        return await self.repository.update(id, **kwargs)
