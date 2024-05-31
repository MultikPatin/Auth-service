from uuid import UUID

from src.api.models.db.base import BaseMixin


class RolePermissionDB(BaseMixin):
    role_uuid: UUID
    permission_uuid: UUID
