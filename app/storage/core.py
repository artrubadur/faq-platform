from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import app.storage.models  # noqa: F401
from app.core.config import config
from app.storage.base import Base

database_url = f"postgresql+asyncpg://{config.db_user}:{config.db_pass}@{config.db_host}:5432/{config.db_name}"
engine = create_async_engine(database_url)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    logger.debug("Initializing the database")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.debug("Tables created")
    logger.info("The database is initialized")


async def close_db():
    logger.debug("Closing the database")
    await engine.dispose()
    logger.info("The database connection pool closed")
