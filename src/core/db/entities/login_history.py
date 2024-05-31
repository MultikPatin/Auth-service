from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.db.entities import Entity

if TYPE_CHECKING:
    from src.core.db.entities import User


class LoginHistory(Entity):
    __tablename__ = "login_history"

    user_uuid: Mapped[UUID(as_uuid=True)] = mapped_column(
        ForeignKey("users.uuid")
    )
    ip_address: Mapped[str] = mapped_column(String(64))
    user_agent: Mapped[str] = mapped_column(String(255))

    user: Mapped["User"] = relationship(
        "User",
        back_populates="login_history",
    )
