from abc import ABC, abstractmethod
from typing import Any, TypeVar

from pydantic import BaseModel

AbstractBaseModel = TypeVar("AbstractBaseModel", bound=BaseModel)


class AbstractModelOauthClient(ABC):
    """
    Abstract base class for oauth.

    Provides an interface for oauth.
    """

    @abstractmethod
    async def create_authorization_url(
        self,
    ) -> None:
        """
        Generate url for oauth authorization.

        Returns:
            valid_authorization_url (str): url for oauth authorization.

        """
        raise NotImplementedError

    @abstractmethod
    async def fetch_token(self, authorization_response: str) -> dict:
        """
        Fetch tokens from oauth response url.

        Args:
            authorization_response (str): Google response url.

        Returns:
            response (dict): Google response with tokens

        """
        raise NotImplementedError

    @abstractmethod
    async def get_claims(self, JWT_token: str) -> Any:
        """
        Get user info from JWT.

        Args:
            JWT_token (str): Oauth JWT, with user info.

        Returns:
            claims (Any): User info.

        """
        raise NotImplementedError
