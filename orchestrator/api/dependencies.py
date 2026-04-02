from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from orchestrator.core.config import config
from orchestrator.db.session import async_session
from orchestrator.integrations import embedding_provider, rerank_provider
from orchestrator.repositories import QuestionsRepository, UsersRepository
from orchestrator.services import QuestionsService, UsersService


async def get_db_session() -> AsyncIterator[AsyncSession]:
    async with async_session() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_db_session)]


def get_users_repository(session: SessionDep) -> UsersRepository:
    return UsersRepository(session)


UsersRepositoryDep = Annotated[UsersRepository, Depends(get_users_repository)]


def get_users_service(
    repository: Annotated[UsersRepository, Depends(get_users_repository)],
) -> UsersService:
    return UsersService(repository)


UsersServiceDep = Annotated[UsersService, Depends(get_users_service)]


def get_questions_repository(session: SessionDep) -> QuestionsRepository:
    return QuestionsRepository(session)


QuestionsRepositoryDep = Annotated[
    QuestionsRepository, Depends(get_questions_repository)
]


def get_questions_service(
    repository: Annotated[QuestionsRepository, Depends(get_questions_repository)],
) -> QuestionsService:
    return QuestionsService(
        repository,
        embedding_provider,
        rerank_provider,
        config.search.best_match_threshold,
        config.search.related_threshold,
    )


QuestionsServiceDep = Annotated[QuestionsService, Depends(get_questions_service)]
