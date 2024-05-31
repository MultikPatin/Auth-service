from functools import lru_cache
from http import HTTPStatus

from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.auth_jwt import AuthJWTBearer
from fastapi import Depends, HTTPException, Request
from fastapi.responses import Response

from src.auth.cache.redis import RedisCache, get_redis
from src.auth.core.config import settings
from src.auth.models.db.token import UserClaims
from src.auth.oauth_clients.google import OauthGoogle, get_google
from src.auth.services.base_oauth2 import BaseService
from src.auth.utils.tokens import TokenUtils, get_token
from src.core.db.repositories.login_history import (
    LoginHistoryRepository,
    get_login_history_repository,
)
from src.core.db.repositories.social_account import (
    SocialAccountRepository,
    get_social_account,
)
from src.core.db.repositories.user import UserRepository, get_user_repository

auth_dep = AuthJWTBearer()


class OAuth2Service(BaseService):
    def __init__(
        self,
        cache: RedisCache,
        google_oauth_client: OauthGoogle,
        user_repository: UserRepository,
        history_repository: LoginHistoryRepository,
        social_account_repository: SocialAccountRepository,
        authorize: AuthJWT,
        token: TokenUtils,
    ):
        super().__init__(
            cache,
            user_repository,
            history_repository,
            social_account_repository,
            authorize,
            token,
        )
        self._google_oauth_client = google_oauth_client

    async def get_google_authorization_url(self) -> str:
        return await self._google_oauth_client.create_authorization_url()

    async def auth_via_google(
        self, request: Request, response: Response
    ) -> dict | UserClaims:
        if (
            request.query_params.get("state")
            != settings.google.google_state.get_secret_value()
        ):
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="Invalid state parameter.",
            )

        authorization_response = str(request.url)
        response = await self._google_oauth_client.fetch_token(
            authorization_response
        )

        id_token = response.get("id_token")
        claims = await self._google_oauth_client.get_claims(id_token)

        return await self.check_social_account(claims)


@lru_cache
def get_oauth2_service(
    cache: RedisCache = Depends(get_redis),
    google_oauth_client: OauthGoogle = Depends(get_google),
    user_repository: UserRepository = Depends(get_user_repository),
    history_repository: LoginHistoryRepository = Depends(
        get_login_history_repository
    ),
    social_account_repository: SocialAccountRepository = Depends(
        get_social_account
    ),
    authorize: AuthJWT = Depends(auth_dep),
    token: TokenUtils = Depends(get_token),
) -> OAuth2Service:
    return OAuth2Service(
        cache,
        google_oauth_client,
        user_repository,
        history_repository,
        social_account_repository,
        authorize,
        token,
    )
