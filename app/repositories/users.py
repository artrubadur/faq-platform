from enum import Enum
from typing import cast

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.storage.db.models import User


class UserColumn(Enum):
    ID = "id"
    TELEGRAM_ID = "telegram_id"
    USERNAME = "username"
    ROLE = "role"


class UsersRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, telegram_id: int, username: str | None, role: str) -> User:
        user = User(telegram_id=telegram_id, username=username, role=role)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get(self, id: int) -> User:
        user = await self.session.execute(select(User).where(User.telegram_id == id))
        return user.scalar_one()

    async def get_slice(self, offset: int, limit: int, order_by: str, ascending: bool):
        col = getattr(User, order_by)

        if ascending:
            order_expr = col.asc()
        else:
            order_expr = col.desc()

        result = await self.session.execute(
            select(User).order_by(order_expr).offset(offset).limit(limit)
        )
        return result.scalars().all()

    async def get_amount(self) -> int:
        count = cast(
            int, await self.session.scalar(select(func.count()).select_from(User))
        )
        return count

    async def update(self, id: int, **kwargs) -> User:
        user = await self.get(id)
        for key, value in kwargs.items():
            setattr(user, key, value)
        await self.session.commit()
        return user

    async def delete(self, id: int):
        user = await self.get(id)
        await self.session.delete(user)
        await self.session.commit()
        return user
