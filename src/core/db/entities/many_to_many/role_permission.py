from sqlalchemy import ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db.entities import Entity


class RolePermission(Entity):
    __tablename__ = "roles_permissions"

    role_uuid: Mapped[UUID(as_uuid=True)] = mapped_column(
        ForeignKey("roles.uuid", ondelete="CASCADE")
    )
    permission_uuid: Mapped[UUID(as_uuid=True)] = mapped_column(
        ForeignKey("permissions.uuid", ondelete="CASCADE")
    )

    __table_args__ = (
        Index("role_permission", "permission_uuid", "role_uuid", unique=True),
    )
