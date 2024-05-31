import random
import string
from functools import lru_cache
from http import HTTPStatus

from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.auth_jwt import AuthJWTBearer
from fastapi import Depends, HTTPException, Request
from fastapi.responses import Response
from werkzeug.security import generate_password_hash

from src.auth.cache.redis import RedisCache, get_redis
from src.auth.core.config import settings
from src.auth.models.api.v1.login_history import RequestLoginHistory
from src.auth.models.api.v1.social_account import RequestSocialAccount
from src.auth.models.api.v1.users import RequestUserCreate
from src.auth.models.db.token import UserClaims
from src.auth.models.db.user import UserDB
from src.auth.oauth_clients.google import OauthGoogle, get_google
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


class OAuth2Service:
    def __init__(
        self,
        cache: RedisCache,
        oauth_client: OauthGoogle,
        user_repository: UserRepository,
        history_repository: LoginHistoryRepository,
        social_account_repository: SocialAccountRepository,
        authorize: AuthJWT,
        token: TokenUtils,
    ):
        self._cache = cache
        self._oauth_client = oauth_client
        self._user_repository = user_repository
        self._history_repository = history_repository
        self._social_account_repository = social_account_repository
        self._authorize = authorize
        self._token = token

    async def get_authorization_url(self) -> str:
        return await self._oauth_client.create_authorization_url()

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
        response = await self._oauth_client.fetch_token(authorization_response)

        id_token = response.get("id_token")
        claims = await self._oauth_client.get_claims(id_token)

        social_name = claims.get("iss")
        social_id = claims.get("sub")
        social_account = (
            await self._social_account_repository.get_by_social_name_id(
                social_name, social_id
            )
        )
        if not social_account:
            return claims
        else:
            user_uuid = social_account.user.uuid
            return UserClaims(
                user_uuid=str(user_uuid),
                role_uuid=str(social_account.user.role_uuid),
            )

    async def checkin_oauth_user(self, claims: dict) -> UserClaims:
        credentials_needed = RequestUserCreate(
            email=claims.get("email"),
            password=generate_password_hash(
                "".join(
                    random.choices(
                        string.digits
                        + string.ascii_letters
                        + string.punctuation,
                        k=20,
                    )
                )
            ),
            first_name=claims.get("given_name"),
            last_name=claims.get("family_name"),
        )
        obj = await self._user_repository.create(credentials_needed)
        user = UserDB.model_validate(obj, from_attributes=True)
        user_uuid = user.uuid
        await self._social_account_repository.create(
            RequestSocialAccount(
                user_uuid=user.uuid,
                social_name=claims.get("iss"),
                social_id=claims.get("sub"),
            )
        )
        return UserClaims(
            user_uuid=str(user_uuid), role_uuid=str(user.role_uuid)
        )

    async def login(self, request: Request, user_data: UserClaims) -> None:
        user_uuid = user_data.user_uuid
        tokens = await self._token.create_tokens(user_data)
        await self._token.set_tokens_to_cookies(tokens)
        await self._token.delete_oldest_token(user_uuid)
        await self._cache.set_token(user_uuid, tokens.refresh)
        await self._history_repository.create(
            RequestLoginHistory(
                user_uuid=user_uuid,
                ip_address=request.headers.get("Host"),
                user_agent=request.headers.get("User-Agent"),
            )
        )


@lru_cache
def get_oauth2_service(
    cache: RedisCache = Depends(get_redis),
    oauth_client: OauthGoogle = Depends(get_google),
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
        oauth_client,
        user_repository,
        history_repository,
        social_account_repository,
        authorize,
        token,
    )
