from functools import lru_cache
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.auth.models.api.v1.social_account import RequestSocialAccount
from src.core.db.clients.postgres import PostgresDatabase, get_postgres_auth_db
from src.core.db.entities import SocialAccount
from src.core.db.repositories.base import (
    InitRepository,
)


class SocialAccountRepository(InitRepository):
    async def create(self, instance: RequestSocialAccount) -> SocialAccount:
        async with self._database.get_session() as session:
            db_obj = self._model(**instance.model_dump())
            session.add(db_obj)
            await session.commit()
            await session.refresh(db_obj)
            return db_obj

    async def get_by_social_name_id(
        self, social_name: str, social_id: str
    ) -> UUID | None:
        async with self._database.get_session() as session:
            db_obj = await session.execute(
                select(self._model)
                .where(
                    self._model.social_name == social_name
                    and self._model.social_id == social_id
                )
                .options(selectinload(self._model.user))
            )
            obj_uuid = db_obj.scalars().first()
            return obj_uuid


@lru_cache
def get_social_account(
    database: PostgresDatabase = Depends(get_postgres_auth_db),
) -> SocialAccountRepository:
    return SocialAccountRepository(database, SocialAccount)
