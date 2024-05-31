from pydantic import BaseModel, Field, SecretStr

from src.auth.models.api.base import UUIDMixin
from src.auth.models.api.v1.roles import ResponseRole


class ResponseUserRole(UUIDMixin):
    role: ResponseRole


class RequestPasswordChange(BaseModel):
    new_password: SecretStr = Field(
        description="Новый пароль пользователя",
        example="[2/#&/%M9:aOIzJ-Xb.0Ncod?HoQih",
        min_length=1,
        max_length=255,
    )
    current_password: SecretStr = Field(
        description="Текущий пароль пользователя",
        example="DJVkw6U&}b;q#V-D!7^;zl?52im2*B",
        min_length=1,
        max_length=255,
    )
