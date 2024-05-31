from functools import lru_cache
from typing import Any
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.auth.models.api.v1.roles import (
    RequestRoleCreate,
    RequestRoleUpdate,
)
from src.core.db.clients.postgres import (
    PostgresDatabase,
    get_postgres_auth_db,
)
from src.core.db.entities import Role
from src.core.db.repositories.base import (
    CountRepositoryMixin,
    NameFieldRepositoryMixin,
    PostgresRepository,
)


class RoleRepository(
    PostgresRepository[
        PostgresDatabase,
        Role,
        RequestRoleCreate,
        RequestRoleUpdate,
    ],
    NameFieldRepositoryMixin,
    CountRepositoryMixin,
):
    async def get_with_permissions(self, role_uuid: UUID) -> Any | None:
        async with self._database.get_session() as session:
            db_obj = await session.execute(
                select(self._model)
                .where(self._model.uuid == role_uuid)
                .options(selectinload(self._model.permissions))
            )
            return db_obj.unique().scalars().first()


@lru_cache
def get_role_repository(
    database: PostgresDatabase = Depends(get_postgres_auth_db),
) -> RoleRepository:
    return RoleRepository(database, Role)
