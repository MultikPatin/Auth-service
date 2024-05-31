from pydantic import BaseModel, Field

from src.auth.models.api.base import (
    TimeMixin,
    UUIDMixin,
)
from src.auth.models.api.v1.permissions import (
    ResponsePermissionShort,
)
from src.auth.utils.pagination import PaginatedMixin


class RequestRoleUpdate(BaseModel):
    description: str = Field(
        description="Описание роли",
        example="Премиальный доступ",
        min_length=1,
        max_length=255,
    )


class RequestRoleCreate(RequestRoleUpdate):
    description: str | None = Field(
        description="Описание роли",
        example="Премиальный доступ",
        min_length=1,
        max_length=255,
    )
    name: str = Field(
        description="Наименование роли",
        example="Премиум",
        min_length=1,
        max_length=64,
    )


class RoleBase(RequestRoleUpdate, UUIDMixin, TimeMixin):
    name: str = Field(
        description="Наименование роли",
        example="Премиум",
        min_length=1,
        max_length=64,
    )


class ResponseRole(RequestRoleCreate, UUIDMixin, TimeMixin):
    pass


class ResponseRoleShort(UUIDMixin):
    name: str = Field(
        description="Наименование роли",
        example="Премиум",
        min_length=1,
        max_length=64,
    )


class ResponseRolesPaginated(PaginatedMixin):
    permissions: list[ResponseRoleShort]


class ResponseRoleExtended(ResponseRoleShort):
    permissions: list[ResponsePermissionShort]
