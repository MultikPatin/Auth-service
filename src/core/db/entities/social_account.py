from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.db.entities import Entity

if TYPE_CHECKING:
    from src.core.db.entities import User


class SocialAccount(Entity):
    __tablename__ = "social_accounts"
    user_uuid: Mapped[UUID(as_uuid=True)] = mapped_column(
        ForeignKey("users.uuid", ondelete="CASCADE"), nullable=False
    )
    social_id: Mapped[str] = mapped_column(String(255), nullable=False)
    social_name: Mapped[str] = mapped_column(String(255), nullable=False)
    user: Mapped["User"] = relationship(
        "User",
        back_populates="social_accounts",
    )
    # def __init__(
    #     self,
    #     user_uuid: UUID,
    #     social_id: str,
    #     social_name: str,

    # ) -> None:
    #     self.user_uuid = user_uuid
    #     self.social_id = social_id
    #     self.social_name = social_name
