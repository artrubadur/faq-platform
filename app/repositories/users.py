from enum import Enum
from typing import Sequence, cast

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.storage.models.user import Role, User


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

    async def get_by_id(self, id: int) -> User:
        user = await self.session.execute(select(User).where(User.telegram_id == id))
        return user.scalar_one()

    async def get_by_role(self, role: Role) -> Sequence[User]:
        users = await self.session.execute(select(User).where(User.role == role))
        return users.scalars().all()

    async def get_slice(
        self, offset: int, limit: int, order_by: str, ascending: bool
    ) -> Sequence[User]:
        col = getattr(User, order_by)

        order_expr = col.asc() if ascending else col.desc()

        users = await self.session.execute(
            select(User).order_by(order_expr).offset(offset).limit(limit)
        )
        return users.scalars().all()

    async def get_amount(self) -> int:
        amount = await self.session.execute(select(func.count()).select_from(User))
        return cast(int, amount.scalar())

    async def update(self, id: int, **kwargs) -> User:
        result = await self.session.execute(
            update(User).where(User.telegram_id == id).values(**kwargs).returning(User)
        )
        await self.session.commit()
        return result.scalar_one()

    async def delete(self, id: int) -> User:
        result = await self.session.execute(
            delete(User).where(User.telegram_id == id).returning(User)
        )
        await self.session.commit()
        return result.scalar_one()
