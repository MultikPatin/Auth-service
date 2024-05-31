from functools import lru_cache
from uuid import UUID

from fastapi import Depends

from src.auth.models.api.v1.users import (
    RequestUserCreate,
    RequestUserUpdate,
    ResponseUserExtended,
    ResponseUsersPaginated,
)
from src.auth.models.api.v1.users_additional import RequestPasswordChange
from src.auth.models.db.user import UserDB
from src.auth.services.base import BaseService
from src.core.db.repositories.user import UserRepository, get_user_repository


class UserService(
    BaseService[
        UserDB,
        ResponseUsersPaginated,
        RequestUserCreate,
        RequestUserUpdate,
    ]
):
    _repository: UserRepository

    async def get_role_for_user(self, user_uuid: UUID) -> ResponseUserExtended:
        obj = await self._repository.get_with_role(user_uuid)
        if obj is not None:
            model = ResponseUserExtended.model_validate(
                obj, from_attributes=True
            )
            return model

    async def change_password(
        self, user_uuid: UUID, obj: RequestPasswordChange
    ) -> UserDB | None:
        obj = await self._repository.change_password(user_uuid, obj)
        if obj is not None:
            model = self._model.model_validate(obj, from_attributes=True)
            return model
        return None

    async def change_user_role(
        self, user_uuid: UUID, role_uuid: UUID
    ) -> ResponseUserExtended:
        obj = await self._repository.change_user_role(user_uuid, role_uuid)
        if obj is not None:
            model = ResponseUserExtended.model_validate(
                obj, from_attributes=True
            )
            return model

    async def remove_user_role(self, user_uuid: UUID) -> ResponseUserExtended:
        obj = await self._repository.remove_user_role(user_uuid)
        if obj is not None:
            model = ResponseUserExtended.model_validate(
                obj, from_attributes=True
            )
            return model


@lru_cache
def get_user_service(
    repository: UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(repository, UserDB)
