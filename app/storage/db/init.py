from sqlalchemy import text

from app.storage.db.base import Base
from app.storage.db.engine import engine


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)
