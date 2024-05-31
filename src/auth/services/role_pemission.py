from functools import lru_cache
from uuid import UUID

from fastapi import Depends

from src.auth.models.api.v1.role_pemission import (
    RequestRolePermissionShortCreate,
)
from src.auth.models.api.v1.roles import ResponseRoleExtended
from src.auth.models.db.role_permission import RolePermissionDB
from src.core.db.repositories.many_to_many.role_pemission import (
    RolePermissionRepository,
    get_role_permission_repository,
)
from src.core.db.repositories.permission import (
    PermissionRepository,
    get_permission_repository,
)
from src.core.db.repositories.role import RoleRepository, get_role_repository


class RolePermissionService:
    def __init__(
        self,
        repository: RolePermissionRepository,
        role_repository: RoleRepository,
        permission_repository: PermissionRepository,
    ):
        self._repository = repository
        self._role_repository = role_repository
        self._permission_repository = permission_repository
        self._model = RolePermissionDB

    async def get_permissions_for_role(
        self, obj_uuid: UUID
    ) -> ResponseRoleExtended:
        obj = await self._role_repository.get_with_permissions(obj_uuid)
        if not obj:
            return
        model = ResponseRoleExtended.model_validate(obj, from_attributes=True)
        return model

    async def create_permission_for_role(
        self, obj: RequestRolePermissionShortCreate
    ) -> ResponseRoleExtended:
        obj = await self._repository.create(obj)
        obj = await self._role_repository.get_with_permissions(obj.role_uuid)
        model = ResponseRoleExtended.model_validate(obj, from_attributes=True)
        return model

    async def remove_permission_for_role(
        self, role_uuid: UUID, permission_uuid: UUID
    ) -> None:
        await self._repository.remove(role_uuid, permission_uuid)


@lru_cache
def get_role_permission_service(
    repository: RolePermissionRepository = Depends(
        get_role_permission_repository
    ),
    role_repository: RoleRepository = Depends(get_role_repository),
    permission_repository: PermissionRepository = Depends(
        get_permission_repository
    ),
) -> RolePermissionService:
    return RolePermissionService(
        repository, role_repository, permission_repository
    )
