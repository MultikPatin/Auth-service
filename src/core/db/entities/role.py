from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.db.entities import Entity

if TYPE_CHECKING:
    from src.core.db.entities import User


class Role(Entity):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(64), unique=True)
    description: Mapped[str | None] = mapped_column(String(255))

    user: Mapped[list["User"] | None] = relationship(
        "User",
        back_populates="role",
        order_by="User.uuid.desc()",
    )
    permissions = relationship(
        "Permission",
        secondary="roles_permissions",
        back_populates="roles",
    )
