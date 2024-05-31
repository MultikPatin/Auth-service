from pydantic import Field

from src.core.configs.base import ServiceSettings


class RedisSettings(ServiceSettings):
    """
    This class is used to store the REDIS connection settings.
    """

    host: str = Field(..., alias="REDIS_HOST")
    port: int = Field(..., alias="REDIS_PORT")
    host_local: str = Field(..., alias="REDIS_HOST_LOCAL")
    port_local: int = Field(..., alias="REDIS_PORT_LOCAL")

    @property
    def connection_dict(self) -> dict:
        return {
            "host": self.correct_host(),
            "port": self.correct_port(),
        }


class RedisContentSettings(RedisSettings):
    """
    This class is used to store the REDIS content db connection settings.
    """

    host: str = Field(..., alias="CONTENT_REDIS_HOST")
    port: int = Field(..., alias="CONTENT_REDIS_PORT")
    host_local: str = Field(..., alias="CONTENT_REDIS_HOST_LOCAL")
    port_local: int = Field(..., alias="CONTENT_REDIS_PORT_LOCAL")


class RedisAuthSettings(RedisSettings):
    """
    This class is used to store the REDIS auth db connection settings.
    """

    host: str = Field(..., alias="AUTH_REDIS_HOST")
    port: int = Field(..., alias="AUTH_REDIS_PORT")
    host_local: str = Field(..., alias="AUTH_REDIS_HOST_LOCAL")
    port_local: int = Field(..., alias="AUTH_REDIS_PORT_LOCAL")
