from uuid import UUID

from pydantic import BaseModel, Field, SecretStr


class RequestSocialAccount(BaseModel):
    user_uuid: UUID = Field(
        description="UUID идентификатор пользователя",
        example="3fa85f64-5717-4562-b3fc-2c963f66afa6",
    )
    social_name: str = Field(
        description="Url адрес сервера oauth",
    )
    social_id: str = Field(
        description="Идентификатор пользователя, уникальный среди всех учетных записей сервера oauth",
    )


class RequestPasswordSet(BaseModel):
    password: SecretStr = Field(
        description="Новый пароль пользователя",
        example="[2/#&/%M9:aOIzJ-Xb.0Ncod?HoQih",
        min_length=1,
        max_length=255,
    )
