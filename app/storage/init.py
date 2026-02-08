from loguru import logger
from sqlalchemy import text

from app.storage.base import Base
from app.storage.engine import engine


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        logger.debug("Database vector extension initialized")
        await conn.run_sync(Base.metadata.create_all)
        logger.debug("Database tables created")
    logger.info("Database initialized")
