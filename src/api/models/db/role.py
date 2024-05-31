from src.api.models.db.base import BaseMixin
from src.api.models.db.permission import PermissionDB


class RoleDB(BaseMixin):
    name: str
    description: str | None


class RoleDBExtended(RoleDB):
    permission: list[PermissionDB]
