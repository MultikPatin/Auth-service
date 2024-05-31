import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.core.configs.postgres import (
    PostgresAuthSettings,
    PostgresContentSettings,
)
from src.core.db.clients.abstract import AbstractDBClient
from src.core.utils.sqlalchemy import SQLAlchemyConnectMixin

logger = logging.getLogger(__name__)
logger.level = logging.DEBUG

load_dotenv()


class PostgresContentConnect(PostgresContentSettings, SQLAlchemyConnectMixin):
    pass


async def get_postgres_content_settings() -> PostgresContentConnect:
    return PostgresContentConnect()


class PostgresAuthConnect(PostgresAuthSettings, SQLAlchemyConnectMixin):
    pass


async def get_postgres_auth_settings() -> PostgresAuthConnect:
    return PostgresAuthConnect()


class PostgresDatabase(AbstractDBClient):
    def __init__(self, settings) -> None:
        self._async_session_factory = async_sessionmaker(
            create_async_engine(
                settings.postgres_connection_url, echo=settings.sqlalchemy_echo
            )
        )

    @asynccontextmanager
    async def get_session(self) -> AsyncIterator[AsyncSession]:
        try:
            logger.debug("==> Session open")
            session = self._async_session_factory()
            yield session
        except Exception as error:
            logger.exception("==> Session rollback because of exception", error)
            await session.rollback()
            raise
        finally:
            logger.debug("==> Session close")
            await session.close()


def get_postgres_content_db(
    settings: PostgresContentConnect = Depends(
        get_postgres_content_settings, use_cache=True
    ),
) -> PostgresDatabase:
    return PostgresDatabase(settings)


def get_postgres_auth_db(
    settings: PostgresAuthConnect = Depends(
        get_postgres_auth_settings, use_cache=True
    ),
) -> PostgresDatabase:
    return PostgresDatabase(settings)
