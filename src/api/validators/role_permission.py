from uuid import UUID

from fastapi import Depends, HTTPException

from src.core.db.repositories.many_to_many.role_pemission import (
    RolePermissionRepository,
    get_role_permission_repository,
)


class RolePermissionValidator:
    def __init__(self, repository: RolePermissionRepository):
        self._repository = repository

    async def is_duplicate_row(
        self, role_uuid: UUID, permission_uuid: UUID
    ) -> None:
        permission_uuid = await self._repository.get(role_uuid, permission_uuid)
        if permission_uuid is not None:
            raise HTTPException(
                status_code=400,
                detail="An object with that name already exists",
            )


def get_role_permission_validator(
    repository: RolePermissionRepository = Depends(
        get_role_permission_repository
    ),
) -> RolePermissionValidator:
    return RolePermissionValidator(repository)
