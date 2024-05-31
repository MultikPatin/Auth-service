from datetime import datetime
from http import HTTPStatus
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, SecretStr


class UUIDMixin(BaseModel):
    uuid: UUID = Field(
        description="UUID идентификатор",
        example="3fa85f64-5717-4562-b3fc-2c963f66afa6",
    )

    class Meta:
        abstract = True


class TokenMixin(BaseModel):
    refresh: list[str]

    class Meta:
        abstract = True


class TimeMixin(BaseModel):
    created_at: datetime = Field(
        description="Дата создания записи",
        example="2024-04-19T17:17:31.711Z",
    )
    updated_at: datetime = Field(
        description="Дата последнего редактирования записи",
        example="2024-04-19T19:17:31.711Z",
    )

    class Meta:
        abstract = True


class LoginMixin(BaseModel):
    email: EmailStr = Field(
        description="Email пользователя",
        example="exemple@mail.ru",
        min_length=1,
        max_length=64,
    )
    password: SecretStr = Field(
        description="Пароль пользователя",
        example="[2/#&/%M9:aOIzJ-Xb.0Ncod?HoQih",
        min_length=1,
        max_length=255,
    )

    class Meta:
        abstract = True


class StringRepresent(BaseModel):
    code: HTTPStatus
    details: str
