from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.storage.db.models import User


class UsersRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, telegram_id: int, username: str | None, role: str) -> User:
        user = User(telegram_id=telegram_id, username=username, role=role)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def read(self, id: int) -> User:
        result = await self.session.execute(select(User).where(User.telegram_id == id))
        return result.scalar_one()

    async def update(self, id: int, **kwargs) -> User:
        user = await self.read(id)
        for key, value in kwargs.items():
            setattr(user, key, value)
        await self.session.commit()
        return user

    async def delete(self, id: int):
        user = await self.read(id)
        await self.session.delete(user)
        await self.session.commit()
        return user
