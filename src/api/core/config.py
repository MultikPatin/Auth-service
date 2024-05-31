import os
from logging import config as logging_config

from dotenv.main import find_dotenv, load_dotenv
from pydantic import SecretStr
from pydantic.fields import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.api.core.logger import LOGGING
from src.core.configs.auth_jwt import AuthJWTSettings
from src.core.configs.postgres import PostgresSettings
from src.core.configs.redis import RedisSettings

load_dotenv(find_dotenv(".env"))

logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )
    postgres: PostgresSettings = PostgresSettings()

    redis: RedisSettings = RedisSettings()

    name: str = Field(..., alias="API_PROJECT_NAME")
    description: str = Field(..., alias="API_PROJECT_DESCRIPTION")
    docs_url: str = Field(..., alias="API_DOCS_URL")
    openapi_url: str = Field(..., alias="API_OPENAPI_URL")
    host: str = Field(..., alias="API_HOST")
    port: int = Field(..., alias="API_PORT")

    empty_role_name: str = Field(..., alias="EMPTY_ROLE_NAME")
    empty_role_description: str = Field(..., alias="EMPTY_ROLE_DESCRIPTION")

    admin_email: str = Field(..., alias="ADMIN_EMAIL")
    admin_password: SecretStr = Field(..., alias="ADMIN_PASSWORD")

    token_expire_time: int = Field(..., alias="TOKEN_EXPIRE_TIME")
    user_max_sessions: int = Field(..., alias="USER_MAX_SESSIONS")

    auth_jwt: AuthJWTSettings = AuthJWTSettings()

    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


settings = Settings()
