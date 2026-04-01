from loguru import logger

import orchestrator.db.models  # noqa: F401
from orchestrator.core.config import config
from orchestrator.db.base import Base
from orchestrator.db.migrations.schema_sync import ensure_schema_constraints
from orchestrator.db.session import engine


async def init_db():
    logger.debug("Initializing the database")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.debug("Tables created")
    await ensure_schema_constraints(
        config.db_schema.question_text_max_len,
        config.db_schema.answer_text_max_len,
        config.db_schema.question_embedding_dim,
    )
    logger.info("The database is initialized")


async def close_db():
    logger.debug("Closing the database")
    await engine.dispose()
    logger.info("The database connection pool closed")
