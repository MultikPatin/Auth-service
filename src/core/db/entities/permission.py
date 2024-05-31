from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.db.entities import Entity


class Permission(Entity):
    __tablename__ = "permissions"

    name: Mapped[str] = mapped_column(String(64), unique=True)
    description: Mapped[str | None] = mapped_column(String(255))

    roles = relationship(
        "Role",
        secondary="roles_permissions",
        back_populates="permissions",
    )
