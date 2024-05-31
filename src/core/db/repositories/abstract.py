from abc import ABC, abstractmethod
from typing import TypeVar
from uuid import UUID

DB = TypeVar("DB")
M = TypeVar("M")


class AbstractRepositoryCD(ABC):
    _database: DB
    _model: M

    @abstractmethod
    async def create(self, instance: M) -> M:
        pass

    @abstractmethod
    async def remove(self, instance: M) -> None:
        pass


class AbstractRepositoryCRD(AbstractRepositoryCD, ABC):
    @abstractmethod
    async def get_all(self) -> list[M] | None:
        pass

    @abstractmethod
    async def get(self, instance_id: UUID) -> M | None:
        pass


class AbstractRepository(AbstractRepositoryCRD, ABC):
    @abstractmethod
    async def update(self, instance_id: UUID, instance: M) -> M:
        pass

    @abstractmethod
    async def count(self) -> int:
        pass
