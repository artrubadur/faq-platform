from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from orchestrator.core.config import config
from orchestrator.db.session import async_session
from orchestrator.integrations import (
    compose_provider,
    embedding_provider,
    rerank_provider,
)
from orchestrator.repositories import (
    FormulationsRepository,
    QuestionsRepository,
    UsersRepository,
)
from orchestrator.services import FormulationsService, QuestionsService, UsersService


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


def get_formulations_repository(
    session: SessionDep,
) -> FormulationsRepository:
    return FormulationsRepository(session)


FormulationsRepositoryDep = Annotated[
    FormulationsRepository,
    Depends(get_formulations_repository),
]


def get_questions_service(
    questions_repository: Annotated[
        QuestionsRepository, Depends(get_questions_repository)
    ],
    formulations_repository: Annotated[
        FormulationsRepository, Depends(get_formulations_repository)
    ],
) -> QuestionsService:
    return QuestionsService(
        questions_repository,
        formulations_repository,
        embedding_provider,
        rerank_provider,
        compose_provider,
        config.suggestion.search.best_match_threshold,
        config.suggestion.search.related_threshold,
    )


QuestionsServiceDep = Annotated[QuestionsService, Depends(get_questions_service)]


def get_formulations_service(
    repository: Annotated[FormulationsRepository, Depends(get_formulations_repository)],
    questions_repository: Annotated[
        QuestionsRepository, Depends(get_questions_repository)
    ],
) -> FormulationsService:
    return FormulationsService(
        repository,
        questions_repository,
        embedding_provider,
    )


FormulationsServiceDep = Annotated[
    FormulationsService, Depends(get_formulations_service)
]
