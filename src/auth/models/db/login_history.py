from uuid import UUID

from src.auth.models.db.base import BaseMixin


class LoginHistoryDB(BaseMixin):
    user_uuid: UUID
    ip_address: str
    user_agent: str
