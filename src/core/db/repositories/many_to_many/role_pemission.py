from uuid import UUID

from fastapi import Depends
from sqlalchemy import and_, delete, select

from src.auth.models.api.v1.role_pemission import (
    RequestRolePermissionShortCreate,
)
from src.core.db.clients.postgres import (
    PostgresDatabase,
    get_postgres_auth_db,
)
from src.core.db.entities import RolePermission
from src.core.db.repositories.many_to_many.base import (
    ManyToManyPostgresRepository,
)


class RolePermissionRepository(
    ManyToManyPostgresRepository[
        RolePermission, RequestRolePermissionShortCreate
    ]
):
    async def remove(self, role_uuid: UUID, permission_uuid: UUID) -> None:
        async with self._database.get_session() as session:
            await session.execute(
                delete(self._model).where(
                    and_(
                        self._model.role_uuid == role_uuid,
                        self._model.permission_uuid == permission_uuid,
                    )
                )
            )
            await session.commit()

    async def get(
        self, role_uuid: UUID, permission_uuid: UUID
    ) -> RolePermission | None:
        async with self._database.get_session() as session:
            db_obj = await session.execute(
                select(self._model).where(
                    and_(
                        self._model.role_uuid == role_uuid,
                        self._model.permission_uuid == permission_uuid,
                    )
                )
            )
            return db_obj.scalars().first()


def get_role_permission_repository(
    database: PostgresDatabase = Depends(get_postgres_auth_db),
) -> RolePermissionRepository:
    return RolePermissionRepository(database, RolePermission)
