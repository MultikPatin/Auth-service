from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel

from src.core.db.repositories.abstract import AbstractRepository

DBSchemaType = TypeVar("DBSchemaType", bound=BaseModel)
DBSchemaPaginationType = TypeVar("DBSchemaPaginationType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class InitService:
    _model: DBSchemaType

    def __init__(
        self, repository: AbstractRepository, model: type[DBSchemaType]
    ):
        self._repository = repository
        self._model = model


class BaseService(
    InitService,
    Generic[
        DBSchemaType, DBSchemaPaginationType, CreateSchemaType, UpdateSchemaType
    ],
):
    async def get(self, obj_uuid: UUID) -> DBSchemaType | None:
        obj = await self._repository.get(obj_uuid)
        if obj is None:
            return None
        model = self._model.model_validate(obj, from_attributes=True)
        return model

    async def get_all(self) -> list[DBSchemaType] | None:
        objs = await self._repository.get_all()
        if objs is None:
            return None
        models = [
            self._model.model_validate(obj, from_attributes=True)
            for obj in objs
        ]
        return models

    async def create(self, obj: CreateSchemaType) -> DBSchemaType:
        obj = await self._repository.create(obj)
        model = self._model.model_validate(obj, from_attributes=True)
        return model

    async def update(
        self, obj_uuid: UUID, obj: UpdateSchemaType
    ) -> DBSchemaType:
        obj = await self._repository.update(obj_uuid, obj)
        model = self._model.model_validate(obj, from_attributes=True)
        return model

    async def remove(self, obj_uuid: UUID) -> None:
        obj_uuid = await self._repository.remove(obj_uuid)
        return obj_uuid

    async def count(self) -> int:
        count = await self._repository.count()
        return count
