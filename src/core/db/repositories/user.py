from functools import lru_cache
from typing import Any
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.auth.core.config import settings
from src.auth.models.api.v1.users import RequestUserCreate, RequestUserUpdate
from src.auth.models.api.v1.users_additional import RequestPasswordChange
from src.core.db.clients.postgres import (
    PostgresDatabase,
    get_postgres_auth_db,
)
from src.core.db.entities import User
from src.core.db.repositories.base import (
    CountRepositoryMixin,
    EmailFieldRepositoryMixin,
    PostgresRepository,
)
from src.core.db.repositories.role import RoleRepository, get_role_repository


class UserRepository(
    PostgresRepository[
        PostgresDatabase, User, RequestUserCreate, RequestUserUpdate
    ],
    EmailFieldRepositoryMixin,
    CountRepositoryMixin,
):
    def __init__(
        self,
        database: PostgresDatabase,
        model: type[User],
        role_repository: RoleRepository,
    ):
        super().__init__(database, model)
        self.role_repository = role_repository

    async def create(self, instance: RequestUserCreate) -> User:
        async with self._database.get_session() as session:
            role_uuid = await self.role_repository.get_uuid_by_name(
                settings.empty_role_name
            )
            create_dict = instance.dict()
            create_dict["role_uuid"] = role_uuid
            db_obj = self._model(**create_dict)
            session.add(db_obj)
            await session.commit()
            await session.refresh(db_obj)
            return db_obj

    async def get_with_role(self, user_uuid: UUID) -> Any | None:
        async with self._database.get_session() as session:
            db_obj = await session.execute(
                select(self._model)
                .where(self._model.uuid == user_uuid)
                .options(joinedload(self._model.role))
            )
            return db_obj.unique().scalars().first()

    async def change_password(
        self, user_uuid: UUID, obj: RequestPasswordChange
    ) -> User | None:
        async with self._database.get_session() as session:
            user = await self.get(user_uuid)
            if user.check_password(obj.current_password.get_secret_value()):
                user.password = obj.new_password.get_secret_value()
                session.add(user)
                await session.commit()
                await session.refresh(user)
                return user
            return None

    async def change_user_role(self, user_uuid: UUID, role_uuid: UUID) -> Any:
        async with self._database.get_session() as session:
            user = await self.get(user_uuid)
            user.role_uuid = role_uuid
            session.add(user)
            await session.commit()
            return await self.get_with_role(user_uuid)


@lru_cache
def get_user_repository(
    database: PostgresDatabase = Depends(get_postgres_auth_db),
    role_repository: RoleRepository = Depends(get_role_repository),
) -> UserRepository:
    return UserRepository(database, User, role_repository)
