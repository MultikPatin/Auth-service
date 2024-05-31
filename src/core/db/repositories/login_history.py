from functools import lru_cache
from typing import TypeVar
from uuid import UUID

from fastapi import Depends
from sqlalchemy import func, select

from src.auth.models.api.v1.login_history import RequestLoginHistory
from src.core.db.clients.postgres import (
    PostgresDatabase,
    get_postgres_auth_db,
)
from src.core.db.entities import LoginHistory
from src.core.db.repositories.base import InitRepository

ModelType = TypeVar("ModelType", bound=LoginHistory)


class LoginHistoryRepository(InitRepository):
    async def create(self, instance: RequestLoginHistory) -> ModelType:
        async with self._database.get_session() as session:
            db_obj = self._model(**instance.dict())
            session.add(db_obj)
            await session.commit()
            await session.refresh(db_obj)
            return db_obj

    async def get_by_user(
        self, user_uuid: UUID, **kwargs
    ) -> list[ModelType] | None:
        limit = kwargs.get("limit")
        offset = kwargs.get("offset")
        async with self._database.get_session() as session:
            query = (
                select(self._model)
                .where(self._model.user_uuid == user_uuid)
                .order_by(self._model.created_at.desc())
            )
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.offset(offset)
            db_obj = await session.execute(query)
            return db_obj.scalars().all()

    async def count(self, **kwargs) -> int | None:
        async with self._database.get_session() as session:
            db_obj = await session.execute(
                select(func.count())
                .select_from(self._model)
                .filter_by(**kwargs)
            )
            return db_obj.scalars().first()


@lru_cache
def get_login_history_repository(
    database: PostgresDatabase = Depends(get_postgres_auth_db),
) -> LoginHistoryRepository:
    return LoginHistoryRepository(database, LoginHistory)
