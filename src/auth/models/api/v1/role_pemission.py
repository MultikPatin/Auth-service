from uuid import UUID

from pydantic import BaseModel


class RequestRolePermissionShortCreate(BaseModel):
    role_uuid: UUID
    permission_uuid: UUID
