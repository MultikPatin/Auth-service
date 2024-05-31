from pydantic import Field

from src.core.configs.base import ServiceSettings


class ElasticSettings(ServiceSettings):
    """
    This class is used to store the Elastic connection settings.
    """

    host: str = Field(..., alias="ELASTIC_HOST")
    port: int = Field(..., alias="ELASTIC_PORT")
    host_local: str = Field("localhost", alias="ELASTIC_HOST_LOCAL")
    port_local: int = Field(9200, alias="ELASTIC_PORT_LOCAL")

    @property
    def get_host(self) -> str:
        return f"http://{self.correct_host()}:{self.correct_port()}"


class ElasticContentSettings(ElasticSettings):
    """
    This class is used to store the Elastic connection settings.
    """

    host: str = Field(..., alias="CONTENT_ELASTIC_HOST")
    port: int = Field(..., alias="CONTENT_ELASTIC_PORT")
    host_local: str = Field(..., alias="CONTENT_ELASTIC_HOST_LOCAL")
    port_local: int = Field(..., alias="CONTENT_ELASTIC_PORT_LOCAL")
