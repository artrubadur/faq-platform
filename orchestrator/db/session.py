from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from orchestrator.core.config import config

database_url = f"postgresql+asyncpg://{config.db.user}:{config.db.password}@{config.db.host}:5432/{config.db.name}"
engine = create_async_engine(database_url)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
