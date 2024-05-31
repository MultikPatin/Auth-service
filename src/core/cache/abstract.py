from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import TypeVar
from uuid import UUID

from pydantic import BaseModel

AbstractBaseModel = TypeVar("AbstractBaseModel", bound=BaseModel)


class AbstractCache(ABC):
    @abstractmethod
    def build_key(self, key_prefix: str, *args: Sequence) -> str:
        """
        Build a cache key.

        Args:
            key_prefix (str): The prefix to use for the cache key.
            *args: Additional arguments to include in the cache key.

        Returns:
            The built cache key.
        """
        raise NotImplementedError


class AbstractAuthCache(AbstractCache):
    """
    Abstract base class for auth caching.
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


class AbstractModelCache(AbstractCache):
    """
    Abstract base class for model caching.
    """

    @abstractmethod
    async def set_one_model(
        self,
        key: str,
        value: AbstractBaseModel,
        cache_expire: int,
    ) -> None:
        """
        Set a single model in the cache.

        Args:
            key (str): The key to use for caching the model.
            value (AbstractBaseModel): The model to cache.
            cache_expire (int): The number of seconds until the model expires.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_one_model(
        self, key: str, model: type[AbstractBaseModel]
    ) -> AbstractBaseModel | None:
        """
        Get a single model from the cache.

        Args:
            key (str): The key used for caching the model.
            model (AbstractBaseModel): The model class to cast the cached value to.

        Returns:
            The cached model, or None if the model is not in the cache.
        """
        raise NotImplementedError

    @abstractmethod
    async def set_list_model(
        self,
        key: str,
        values: list[AbstractBaseModel],
        cache_expire: int,
    ) -> None:
        """
        Set a list of models in the cache.

        Args:
            key (str): The key to use for caching the list of models.
            values (list[AbstractBaseModel]): The list of models to cache.
            cache_expire (int): The number of seconds until the list of models expires.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_list_model(
        self, key: str, model: type[AbstractBaseModel]
    ) -> list[AbstractBaseModel] | None:
        """
        Get a list of models from the cache.

        Args:
            key (str): The key used for caching the list of models.
            model (AbstractBaseModel): The model class to cast the cached values to.

        Returns:
            The cached list of models, or None if the list of models is not in the cache.
        """
        raise NotImplementedError
