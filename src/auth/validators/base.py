from typing import Generic, TypeVar
from uuid import UUID

from fastapi import HTTPException

from src.core.db.entities import Entity
from src.core.db.repositories.abstract import AbstractRepository

Repository = TypeVar("Repository", bound=AbstractRepository)
ModelType = TypeVar("ModelType", bound=Entity)


class BaseValidator(
    Generic[Repository, ModelType],
):
    def __init__(self, repository: Repository):
        self._repository = repository

    async def is_exists(
        self,
        instance_uuid: UUID,
    ) -> UUID:
        instance = await self._repository.get(instance_uuid)
        if instance is None:
            raise HTTPException(
                status_code=404, detail="The object was not found"
            )
        return instance_uuid


class DuplicateNameValidatorMixin:
    _repository: Repository = None

    async def is_duplicate_name(self, name: str) -> None:
        permission_uuid = await self._repository.get_uuid_by_name(name)
        if permission_uuid is not None:
            raise HTTPException(
                status_code=400,
                detail="An object with that name already exists",
            )
