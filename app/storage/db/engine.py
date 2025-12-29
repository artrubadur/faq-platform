from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import app.storage.db.models  # noqa: F401
from app.core.config import DATABASE_URL

engine = create_async_engine(DATABASE_URL)  #  pyright: ignore[reportArgumentType]
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
