from uuid import UUID

from pydantic import EmailStr

from src.auth.models.db.base import BaseMixin


class UserDB(BaseMixin):
    email: EmailStr
    first_name: str | None
    last_name: str | None
    is_superuser: bool = False
    role_uuid: UUID | None
