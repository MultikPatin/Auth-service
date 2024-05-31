from logging import Logger

from authlib.integrations.httpx_client import AsyncOAuth2Client
from authlib.jose import JWTClaims, jwt
from authlib.oidc.core import CodeIDToken

from src.auth.core.config import settings
from src.auth.oauth_clients.abstract import AbstractModelOauthClient


class OauthGoogle(AbstractModelOauthClient):
    """
    Клиент для работы api с Google oauth.

    Args:
        google (AsyncOAuth2Client): объект для работы с Google oauth
        logger (Logger): объект для записи в журналы

    """

    __google: AsyncOAuth2Client
    __logger: Logger

    def __init__(self, google: AsyncOAuth2Client, logger: Logger):
        self.__google = google
        self.__logger = logger
        self.__config = settings.google_config

    async def create_authorization_url(
        self,
    ) -> str:
        """
        Создать url для авторизации Google.

        Returns:
            valid_authorization_url (str): url для авторизации Google.

        """
        authorization_endpoint = self.__config.get("authorization_endpoint")
        authorization_url, _ = self.__google.create_authorization_url(
            authorization_endpoint,
            state=settings.google.google_state.get_secret_value(),
        )
        valid_authorization_url = authorization_url + "&access_type=offline"
        return valid_authorization_url

    async def fetch_token(self, authorization_response: str) -> dict:
        """
        Получить токены из Google response url.

        Args:
            authorization_response (str): Google response url.

        Returns:
            response (dict): Google response, содержащий токены.

        """
        access_token_endpoint = self.__config.get("token_endpoint")
        response = await self.__google.fetch_token(
            access_token_endpoint, authorization_response=authorization_response
        )

        return response

    async def get_claims(self, id_token: str) -> JWTClaims:
        """
        Получить информацию о пользователе из JWT id_token.

        Args:
            id_token (str): Google JWT id_token, содержащий информацию о пользователе.

        Returns:
            claims (JWTClaims): Информация о пользователе.

        """
        jwks_uri = self.__config.get("jwks_uri")
        try:
            keys_response = await self.__google.get(jwks_uri)
        except Exception as set_error:
            self.__logger.error(
                "Error get request with key `%s:`: %s.",
                jwks_uri,
                set_error,
            )
            raise
        keys = keys_response.json()
        claims = jwt.decode(id_token, keys, claims_cls=CodeIDToken)
        claims.validate()
        return claims


google: OauthGoogle | None = None


async def get_google() -> OauthGoogle | None:
    return google
