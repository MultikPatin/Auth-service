from functools import lru_cache
from typing import TypeVar
from uuid import UUID

from fastapi import Depends

from src.auth.models.api.v1.login_history import RequestLoginHistory
from src.auth.models.db.login_history import LoginHistoryDB
from src.core.db.repositories.login_history import (
    LoginHistoryRepository,
    get_login_history_repository,
)

DBSchemaType = TypeVar("DBSchemaType", bound=LoginHistoryDB)


class LoginHistoryService:
    _model: DBSchemaType

    def __init__(
        self, repository: LoginHistoryRepository, model: type[DBSchemaType]
    ):
        self._repository = repository
        self._model = model

    async def create(self, obj: RequestLoginHistory) -> DBSchemaType:
        obj = await self._repository.create(obj)
        model = self._model.model_validate(obj, from_attributes=True)
        return model

    async def get_by_user(
        self, user_uuid: UUID, **kwargs
    ) -> list[DBSchemaType] | None:
        objs = await self._repository.get_by_user(user_uuid, **kwargs)
        if objs is None:
            return None
        models = [
            self._model.model_validate(obj, from_attributes=True)
            for obj in objs
        ]
        return models

    async def count(self, **kwargs) -> int:
        count = await self._repository.count(**kwargs)
        return count


@lru_cache
def get_login_history_service(
    repository: LoginHistoryRepository = Depends(get_login_history_repository),
) -> LoginHistoryService:
    return LoginHistoryService(repository, LoginHistoryDB)
