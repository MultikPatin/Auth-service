from typing import Generic, TypeVar
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import delete, func, select

from src.core.db.clients.postgres import PostgresDatabase
from src.core.db.entities import Entity
from src.core.db.repositories.abstract import AbstractRepository

ModelType = TypeVar("ModelType", bound=Entity)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
D = TypeVar("D", bound=PostgresDatabase)


class InitRepository:
    _database: D
    _model: ModelType

    def __init__(self, database: D, model: type[ModelType]):
        self._database = database
        self._model = model


class PostgresRepository(
    InitRepository,
    AbstractRepository,
    Generic[D, ModelType, CreateSchemaType, UpdateSchemaType],
):
    async def create(self, instance: CreateSchemaType) -> ModelType:
        async with self._database.get_session() as session:
            db_obj = self._model(**instance.dict())
            session.add(db_obj)
            await session.commit()
            await session.refresh(db_obj)
            return db_obj

    async def get_all(self) -> list[ModelType] | None:
        async with self._database.get_session() as session:
            db_objs = await session.execute(select(self._model))
            return db_objs.scalars().all()

    async def get(self, instance_uuid: UUID) -> ModelType | None:
        async with self._database.get_session() as session:
            db_obj = await session.execute(
                select(self._model).where(self._model.uuid == instance_uuid)
            )
            return db_obj.scalars().first()

    async def update(
        self, instance_uuid: UUID, instance: UpdateSchemaType
    ) -> ModelType:
        async with self._database.get_session() as session:
            db_obj = await self.get(instance_uuid)

            obj_data = jsonable_encoder(db_obj)
            update_data = instance.dict(exclude_unset=True)

            for field in obj_data:
                if field in update_data:
                    setattr(db_obj, field, update_data[field])
            session.add(db_obj)
            await session.commit()
            await session.refresh(db_obj)
            return db_obj

    async def remove(self, instance_uuid: UUID) -> UUID:
        async with self._database.get_session() as session:
            await session.execute(
                delete(self._model).where(self._model.uuid == instance_uuid)
            )
            await session.commit()
            return instance_uuid


class NameFieldRepositoryMixin(InitRepository):
    async def get_uuid_by_name(self, name: str) -> UUID | None:
        async with self._database.get_session() as session:
            db_obj = await session.execute(
                select(self._model.uuid).where(self._model.name == name)
            )
            obj_uuid = db_obj.scalars().first()
            return obj_uuid


class EmailFieldRepositoryMixin(InitRepository):
    async def get_uuid_by_email(self, email: str) -> UUID | None:
        async with self._database.get_session() as session:
            db_obj = await session.execute(
                select(self._model.uuid).where(self._model.email == email)
            )
            obj_uuid = db_obj.scalars().first()
            return obj_uuid

    async def get_by_email(self, email: str) -> ModelType | None:
        async with self._database.get_session() as session:
            db_obj = await session.execute(
                select(self._model).where(self._model.email == email)
            )
            return db_obj.scalars().first()


class CountRepositoryMixin(InitRepository):
    async def count(self) -> int | None:
        async with self._database.get_session() as session:
            db_obj = await session.execute(
                select(func.count()).select_from(self._model)
            )
            return db_obj.scalars().first()
