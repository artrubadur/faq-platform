from app.repositories.users import UsersRepository
from app.storage.db.models.user import User


class UsersService:
    def __init__(self, repository: UsersRepository):
        self.repository = repository

    async def create_user(self, id: int, username: str | None, role: str) -> User:
        return await self.repository.create(
            id,
            username,
            role,
        )

    async def read_user(self, id: int) -> User:
        return await self.repository.read(id)

    async def delete_user(self, id: int) -> User:
        return await self.repository.delete(id)

    async def update_user(self, id: int, username: str | None, role: str):
        return await self.repository.update(id, username=username, role=role)
