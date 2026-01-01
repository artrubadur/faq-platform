from app.repositories import UsersRepository
from app.storage.db.models import User


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
        return await self.repository.get(id)

    async def get_user_amount(self) -> int:
        return await self.repository.get_amount()

    async def get_paginated_users(
        self, page: int, page_size: int, order_by: str, ascending: bool
    ) -> list[User]:
        offset = (page - 1) * page_size
        users = await self.repository.get_slice(offset, page_size, order_by, ascending)
        return list(users)

    async def delete_user(self, id: int) -> User:
        return await self.repository.delete(id)

    async def update_user(self, id: int, username: str | None, role: str) -> User:
        return await self.repository.update(id, username=username, role=role)
