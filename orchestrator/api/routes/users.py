from typing import Annotated

from fastapi import APIRouter, Depends

from orchestrator.api.dependencies import UsersServiceDep
from shared.contracts.user.requests import (
    CreateUserRequest,
    ListUsersRequest,
    UpdateUserRequest,
    UsersByRoleRequest,
)
from shared.contracts.user.responses import UserResponse, UsersAmountResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserResponse)
async def create_user(
    request: CreateUserRequest,
    service: UsersServiceDep,
) -> UserResponse:
    return await service.create_user(request)


@router.get("/count", response_model=UsersAmountResponse)
async def get_users_amount(service: UsersServiceDep) -> UsersAmountResponse:
    return await service.get_user_amount()


@router.get("", response_model=list[UserResponse])
async def get_paginated_users(
    request: Annotated[ListUsersRequest, Depends()],
    service: UsersServiceDep,
) -> list[UserResponse]:
    return await service.get_paginated_users(request)


@router.get("/by-role", response_model=list[UserResponse])
async def get_users_by_role(
    request: Annotated[UsersByRoleRequest, Depends()],
    service: UsersServiceDep,
) -> list[UserResponse]:
    return await service.get_users_by_role(request)


@router.get("/{id}", response_model=UserResponse)
async def get_user(
    id: int,
    service: UsersServiceDep,
) -> UserResponse:
    return await service.get_user(id)


@router.patch("/{id}", response_model=UserResponse)
async def update_user(
    id: int,
    request: UpdateUserRequest,
    service: UsersServiceDep,
) -> UserResponse:
    return await service.update_user(id, request)


@router.delete("/{id}", response_model=UserResponse)
async def delete_user(
    id: int,
    service: UsersServiceDep,
) -> UserResponse:
    return await service.delete_user(id)
