import os

from pydantic import Field
from pydantic_settings import BaseSettings


class ServiceSettings(BaseSettings):
    host: str = ""
    port: int = 0
    host_local: str = ""
    port_local: int = 0
    local: bool = Field("True", alias="LOCAL")

    def correct_host(self) -> str:
        if self.local:
            return self.host_local
        return self.host

    def correct_port(self) -> int:
        if self.local:
            return self.port_local
        return self.port


class ProjectSettings(ServiceSettings):
    debug: bool = Field("True", alias="DEBUG")
    enable_tracer: bool = Field("True", alias="ENABLE_TRACER")
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
