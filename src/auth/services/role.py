from functools import lru_cache

from fastapi import Depends

from src.auth.models.api.v1.roles import (
    RequestRoleCreate,
    RequestRoleUpdate,
    ResponseRolesPaginated,
)
from src.auth.models.db.role import RoleDB
from src.auth.services.base import BaseService
from src.core.db.repositories.role import RoleRepository, get_role_repository


class RoleService(
    BaseService[
        RoleDB,
        ResponseRolesPaginated,
        RequestRoleCreate,
        RequestRoleUpdate,
    ]
):
    pass


@lru_cache
def get_role_service(
    repository: RoleRepository = Depends(get_role_repository),
) -> RoleService:
    return RoleService(repository, RoleDB)
