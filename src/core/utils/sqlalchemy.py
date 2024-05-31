from pydantic import SecretStr
from sqlalchemy import URL

from src.core.configs.base import ServiceSettings


class SQLAlchemyConnectMixin(ServiceSettings):
    database: str
    user: str
    password: SecretStr

    @property
    def postgres_connection_url(self) -> URL:
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.user,
            password=self.password.get_secret_value(),
            host=self.correct_host(),
            port=self.correct_port(),
            database=self.database,
        )
