from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from orchestrator.api import questions_router, users_router
from orchestrator.api.errors import register_exception_handlers
from orchestrator.core import requests_status
from orchestrator.core.config import config
from orchestrator.db.core import close_db, init_db
from orchestrator.db.session import async_session
from orchestrator.integrations.embedding.http_client import close_embedding_http_client
from orchestrator.repositories.users import UsersRepository
from orchestrator.services.user import UsersService


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    await init_db()
    async with async_session() as session:
        users_service = UsersService(UsersRepository(session))
        await users_service.sync_admin_roles(config.db_schema.admins)

    logger.info(requests_status)
    logger.info("Orchestrator is starting")

    yield

    logger.info("Orchestrator stopped by user")
    await close_embedding_http_client()
    await close_db()


app = FastAPI(
    lifespan=lifespan,
    title=config.api.title,
    version=config.api.version,
    docs_url=config.api.docs_url,
    redoc_url=config.api.redoc_url,
    openapi_url=config.api.openapi_url,
)

app.include_router(users_router)
app.include_router(questions_router)

register_exception_handlers(app)
