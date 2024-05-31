from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class BaseMixin(BaseModel):
    uuid: UUID
    created_at: datetime
    updated_at: datetime

    class Meta:
        abstract = True
