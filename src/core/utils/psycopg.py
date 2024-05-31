from psycopg2.extras import DictCursor
from pydantic import SecretStr

from src.core.configs.base import ServiceSettings


class PsycopgConnectMixin(ServiceSettings):
    database: str
    user: str
    password: SecretStr

    @property
    def psycopg2_connect(self) -> dict:
        return {
            "dbname": self.database,
            "user": self.user,
            "password": self.password.get_secret_value(),
            "host": self.correct_host(),
            "port": self.correct_port(),
            "cursor_factory": DictCursor,
        }
