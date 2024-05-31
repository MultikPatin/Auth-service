from logging import config as logging_config

from async_fastapi_jwt_auth import AuthJWT
from dotenv import load_dotenv
from pydantic import Field, SecretStr
from pydantic_settings import SettingsConfigDict

from src.auth.configs.google import GoogleSettings
from src.auth.configs.loader import LoaderSettings
from src.auth.core.logger import LOGGING
from src.core.configs.base import ProjectSettings
from src.core.configs.postgres import PostgresAuthSettings
from src.core.configs.redis import RedisAuthSettings
from src.core.utils.sqlalchemy import SQLAlchemyConnectMixin

logging_config.dictConfig(LOGGING)

load_dotenv()


class PostgresAuthConnect(PostgresAuthSettings, SQLAlchemyConnectMixin):
    pass


class Settings(ProjectSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    postgres: PostgresAuthConnect = PostgresAuthConnect()

    redis: RedisAuthSettings = RedisAuthSettings()

    loader: LoaderSettings = LoaderSettings()

    name: str = Field(..., alias="AUTH_PROJECT_NAME")
    description: str = Field(..., alias="AUTH_PROJECT_DESCRIPTION")
    host: str = Field(..., alias="AUTH_API_HOST")
    port: int = Field(..., alias="AUTH_API_PORT")
    docs_url: str = Field(..., alias="AUTH_API_DOCS_URL")
    openapi_url: str = Field(..., alias="AUTH_API_OPENAPI_URL")

    empty_role_name: str = Field(..., alias="AUTH_EMPTY_ROLE_NAME")
    empty_role_description: str = Field(
        ..., alias="AUTH_EMPTY_ROLE_DESCRIPTION"
    )

    admin_email: str = Field(..., alias="AUTH_ADMIN_EMAIL")
    admin_password: SecretStr = Field(..., alias="AUTH_ADMIN_PASSWORD")

    token_expire_time: int = Field(..., alias="AUTH_TOKEN_EXPIRE_TIME")
    user_max_sessions: int = Field(..., alias="AUTH_USER_MAX_SESSIONS")

    authjwt_secret_key: str = Field(..., alias="AUTH_AUTHJWT_SECRET_KEY")
    authjwt_algorithm: str = Field(..., alias="AUTH_AUTHJWT_ALGORITHM")
    authjwt_token_location: set = {"cookies"}
    authjwt_cookie_csrf_protect: bool = (
        Field(..., alias="AUTH_AUTHJWT_COOKIE_CSRF_PROTECT") == "True"
    )
    authjwt_cookie_secure: bool = (
        Field(..., alias="AUTH_AUTHJWT_COOKIE_SECURE") == "True"
    )

    google: GoogleSettings = GoogleSettings()
    google_config: dict = loader.get_JSON_config(loader.google_url)


settings = Settings()


@AuthJWT.load_config
def get_config():
    return Settings()


if settings.debug:
    print(settings.model_dump())
