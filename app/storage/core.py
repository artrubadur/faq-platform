from loguru import logger
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import app.storage.models  # noqa: F401
from app.bot.instance import bot, dp
from app.core.config import config
from app.storage.base import Base
from app.storage.models.user import Role, User
from app.utils.state.data import update_data

database_url = f"postgresql+asyncpg://{config.db_user}:{config.db_pass}@{config.db_host}:5432/{config.db_name}"
engine = create_async_engine(database_url)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    logger.debug("Initializing the database")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.debug("Tables created")
    logger.info("The database is initialized")


async def sync_admin_roles():
    admin_ids = set(config.tg_admins)

    logger.debug(
        "Synchronizing admin access",
        admin_count=len(admin_ids),
        admin_ids=sorted(admin_ids),
    )

    async with async_session() as session:
        promoted = await session.execute(
            update(User)
            .where(User.telegram_id.in_(admin_ids))
            .values(role=Role.ADMIN)
            .returning(User.telegram_id)
        )
        promoted_admins = promoted.scalars().all()

        demoted = await session.execute(
            update(User)
            .where(User.role == Role.ADMIN)
            .where(~User.telegram_id.in_(admin_ids))
            .values(role=Role.USER)
            .returning(User.telegram_id)
        )
        demoted_admins = demoted.scalars().all()

        await session.commit()

    for id in promoted_admins:
        await update_data(bot, dp, id, {"sender_role": Role.ADMIN}, "long")

    logger.info(
        "Admin access synchronized",
        promoted=promoted_admins,
        demoted=demoted_admins,
    )


async def close_db():
    logger.debug("Closing the database")
    await engine.dispose()
    logger.info("The database connection pool closed")
