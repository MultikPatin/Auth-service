from dotenv import load_dotenv
from pydantic import SecretStr
from pydantic.fields import Field

from src.core.configs.base import ServiceSettings

load_dotenv()


class PostgresContentSettings(ServiceSettings):
    """
    This class is used to store the Postgres content db connection settings.
    """

    database: str = Field(..., alias="CONTENT_POSTGRES_DB")
    user: str = Field(..., alias="CONTENT_POSTGRES_USER")
    password: SecretStr = Field(..., alias="CONTENT_POSTGRES_PASSWORD")
    host: str = Field(..., alias="CONTENT_POSTGRES_HOST")
    port: int = Field(..., alias="CONTENT_POSTGRES_PORT")
    host_local: str = Field(..., alias="CONTENT_POSTGRES_HOST_LOCAL")
    port_local: int = Field(..., alias="CONTENT_POSTGRES_PORT_LOCAL")
    sqlalchemy_echo: bool = Field("True", alias="CONTENT_SQLALCHEMY_ECHO")


class PostgresAuthSettings(ServiceSettings):
    """
    This class is used to store the Postgres auth db connection settings.
    """

    database: str = Field(..., alias="AUTH_POSTGRES_DB")
    user: str = Field(..., alias="AUTH_POSTGRES_USER")
    password: SecretStr = Field(..., alias="AUTH_POSTGRES_PASSWORD")
    host: str = Field(..., alias="AUTH_POSTGRES_HOST")
    port: int = Field(..., alias="AUTH_POSTGRES_PORT")
    host_local: str = Field(..., alias="AUTH_POSTGRES_HOST_LOCAL")
    port_local: int = Field(..., alias="AUTH_POSTGRES_PORT_LOCAL")
    sqlalchemy_echo: bool = Field("True", alias="AUTH_SQLALCHEMY_ECHO")
