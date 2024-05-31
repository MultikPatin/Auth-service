from abc import ABC, abstractmethod
from typing import TypeVar
from uuid import UUID

from pydantic import BaseModel

AbstractBaseModel = TypeVar("AbstractBaseModel", bound=BaseModel)


class AbstractModelCache(ABC):
    """
    Abstract base class for caching.

    Provides an interface for caching objects of type ModelType.
    """

    @abstractmethod
    async def set_token(
        self,
        key: UUID,
        value: str,
    ) -> None:
        """
        Set token in the cache.

        Args:
            key (str): The key to use for caching the token.
            value: str: The token.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_tokens(
        self,
        key: str,
    ) -> list[bytes] | None:
        """
        Get tokens from the cache.

        Args:
            key (str): The key used for caching the tokens.

        Returns:
            The cached tokens, or None if the tokens are not in the cache.
        """
        raise NotImplementedError

    @abstractmethod
    async def delete_tokens(
        self, uuid: UUID | str, token: bytes | str, all: bool = False
    ) -> None:
        """
        Delete tokens from the cache.

        Args:
            uuid (str | uuid): The pattern used for search the tokens to delete; key prefix.
            token (bytes | str): The parameter to build key to delete.
            all (bool) The parameter to switch between single and multiply deletion.

        """
        raise NotImplementedError
