from loguru import logger
from sqlalchemy.exc import IntegrityError, NoResultFound

from orchestrator.db.models.user import Role, User
from orchestrator.repositories.users import UsersRepository
from shared.contracts.user.requests import (
    CreateUserRequest,
    ListUsersRequest,
    UpdateUserRequest,
    UsersByRoleRequest,
)
from shared.contracts.user.responses import UserResponse, UsersAmountResponse
from shared.http.exceptions import ConflictError, ForbiddenError, NotFoundError


class UsersService:
    def __init__(self, repository: UsersRepository):
        self.repository = repository

    def _to_response(self, user: User) -> UserResponse:
        return UserResponse.model_validate(user)

    async def _get_existing_user(self, id: int) -> User:
        try:
            return await self.repository.get_by_id(id)
        except NoResultFound as exc:
            raise NotFoundError(f"User {id} not found") from exc

    async def create_user(self, request: CreateUserRequest) -> UserResponse:
        try:
            user = await self.repository.create(
                request.id,
                request.username,
                request.role,
            )
        except IntegrityError as exc:
            raise ConflictError("A user with this identity already exists") from exc
        return self._to_response(user)

    async def get_user(self, id: int) -> UserResponse:
        user = await self._get_existing_user(id)
        return self._to_response(user)

    async def get_user_amount(self) -> UsersAmountResponse:
        amount = await self.repository.get_amount()
        return UsersAmountResponse(amount=amount)

    async def get_paginated_users(
        self,
        request: ListUsersRequest,
    ) -> list[UserResponse]:
        offset = (request.page - 1) * request.page_size
        users = await self.repository.get_slice(
            offset,
            request.page_size,
            request.order_by,
            request.ascending,
        )
        return [self._to_response(user) for user in users]

    async def get_users_by_role(
        self,
        request: UsersByRoleRequest,
    ) -> list[UserResponse]:
        users = await self.repository.get_by_role(request.role)
        return [self._to_response(user) for user in users]

    async def delete_user(self, id: int) -> UserResponse:
        user = await self._get_existing_user(id)
        if Role(user.role) == Role.ADMIN:
            raise ForbiddenError("Admin user cannot be deleted")

        try:
            deleted = await self.repository.delete(id)
        except NoResultFound as exc:
            raise NotFoundError(f"User {id} not found") from exc
        return self._to_response(deleted)

    async def update_user(self, id: int, request: UpdateUserRequest) -> UserResponse:
        user = await self._get_existing_user(id)
        if Role(user.role) == Role.ADMIN:
            raise ForbiddenError("Admin user cannot be updated")

        update_fields = {}
        if "username" in request.model_fields_set:
            update_fields["username"] = request.username
        if "role" in request.model_fields_set:
            update_fields["role"] = request.role

        if not update_fields:
            return self._to_response(user)

        try:
            updated = await self.repository.update(id, **update_fields)
        except IntegrityError as exc:
            raise ConflictError(
                "A user with this identity already exists",
            ) from exc
        except NoResultFound as exc:
            raise NotFoundError(f"User {id} not found") from exc
        return self._to_response(updated)

    async def sync_admin_roles(self, admins: list[int]) -> None:
        admin_ids = set(admins)

        logger.debug(
            "Synchronizing admin access",
            admin_count=len(admin_ids),
            admin_ids=sorted(admin_ids),
        )

        promoted_admins, demoted_admins = await self.repository.sync_admin_roles(
            admin_ids
        )

        logger.info(
            "Admin access synchronized",
            promoted=promoted_admins,
            demoted=demoted_admins,
        )
