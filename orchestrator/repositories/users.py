from typing import cast

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from orchestrator.db.models.user import Role, User


class UsersRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        telegram_id: int,
        username: str | None,
        role: Role | str,
    ) -> User:
        user = User(telegram_id=telegram_id, username=username, role=role)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_by_id(self, id: int) -> User:
        user = await self.session.execute(select(User).where(User.telegram_id == id))
        return user.scalar_one()

    async def get_by_role(self, role: Role) -> list[User]:
        users = await self.session.execute(select(User).where(User.role == role))
        return list(users.scalars().all())

    async def get_slice(
        self, offset: int, limit: int, order_by: str, ascending: bool
    ) -> list[User]:
        col = getattr(User, order_by)

        order_expr = col.asc() if ascending else col.desc()

        users = await self.session.execute(
            select(User).order_by(order_expr).offset(offset).limit(limit)
        )
        return list(users.scalars().all())

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

    async def sync_admin_roles(
        self, admin_ids: set[int]
    ) -> tuple[list[int], list[int]]:
        if admin_ids:
            demoted = await self.session.execute(
                update(User)
                .where(User.role == Role.ADMIN)
                .where(~User.telegram_id.in_(admin_ids))
                .values(role=Role.USER)
                .returning(User.telegram_id)
            )
            promoted = await self.session.execute(
                update(User)
                .where(User.telegram_id.in_(admin_ids))
                .values(role=Role.ADMIN)
                .returning(User.telegram_id)
            )
            promoted_admins = list(promoted.scalars().all())
        else:
            demoted = await self.session.execute(
                update(User)
                .where(User.role == Role.ADMIN)
                .values(role=Role.USER)
                .returning(User.telegram_id)
            )
            promoted_admins: list[int] = []

        await self.session.commit()

        demoted_admins = list(demoted.scalars().all())
        return promoted_admins, demoted_admins
