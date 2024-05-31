from functools import lru_cache

from fastapi import Depends

from src.api.models.api.v1.permissions import (
    RequestPermissionCreate,
    RequestPermissionUpdate,
    ResponsePermissionsPaginated,
)
from src.api.models.db.permission import PermissionDB
from src.api.services.base import BaseService
from src.core.db.repositories.permission import (
    PermissionRepository,
    get_permission_repository,
)


class PermissionService(
    BaseService[
        PermissionDB,
        ResponsePermissionsPaginated,
        RequestPermissionCreate,
        RequestPermissionUpdate,
    ]
):
    pass


@lru_cache
def get_permission_service(
    repository: PermissionRepository = Depends(get_permission_repository),
) -> PermissionService:
    return PermissionService(repository, PermissionDB)
