from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import app.storage.models  # noqa: F401
from app.core.config import config

database_url = f"postgresql+asyncpg://{config.db_user}:{config.db_pass}@{config.db_host}:5432/{config.db_name}"
engine = create_async_engine(database_url)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
