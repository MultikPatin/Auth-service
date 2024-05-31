from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession


class AbstractDBClient(ABC):
    @abstractmethod
    @asynccontextmanager
    async def get_session(self) -> AsyncIterator[AsyncSession]:
        pass
