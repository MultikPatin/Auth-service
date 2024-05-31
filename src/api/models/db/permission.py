from src.api.models.db.base import BaseMixin


class PermissionDB(BaseMixin):
    name: str
    description: str | None
