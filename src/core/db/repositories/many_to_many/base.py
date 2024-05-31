from typing import Generic, TypeVar

from pydantic import BaseModel

from src.core.db.clients.postgres import PostgresDatabase
from src.core.db.entities import Entity

ModelType = TypeVar("ModelType", bound=Entity)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)


class ManyToManyPostgresRepository(Generic[ModelType, CreateSchemaType]):
    _database: PostgresDatabase
    _model: ModelType

    def __init__(self, database: PostgresDatabase, model: type[ModelType]):
        self._database = database
        self._model = model

    async def create(self, instance: CreateSchemaType) -> ModelType:
        async with self._database.get_session() as session:
            db_obj = self._model(**instance.dict())
            session.add(db_obj)
            await session.commit()
            await session.refresh(db_obj)
            return db_obj
