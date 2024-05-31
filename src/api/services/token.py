from datetime import datetime, timedelta
from functools import lru_cache
from http import HTTPStatus
from uuid import UUID

from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.auth_jwt import AuthJWTBearer
from fastapi import Depends, HTTPException, Request

from src.api.core.config import settings
from src.api.models.api.v1.login_history import RequestLoginHistory
from src.api.models.api.v1.tokens import RequestLogin
from src.api.models.db.token import CacheTokens, UserClaims
from src.api.validators.token import validate_token
from src.core.cache.redis import RedisCache, get_redis
from src.core.db.repositories.login_history import (
    LoginHistoryRepository,
    get_login_history_repository,
)
from src.core.db.repositories.user import UserRepository, get_user_repository

auth_dep = AuthJWTBearer()


class TokenService:
    def __init__(
        self,
        cache: RedisCache,
        user_repository: UserRepository,
        history_repository: LoginHistoryRepository,
        authorize: AuthJWT,
    ):
        self._cache = cache
        self._user_repository = user_repository
        self._history_repository = history_repository
        self._authorize = authorize

    async def __delete_oldest_token(self, user_uuid: UUID):
        current_cache_tokens = await self._cache.get_tokens(user_uuid)
        if current_cache_tokens is not None and (
            len(current_cache_tokens) >= settings.user_max_sessions
        ):
            oldest = datetime.max
            oldest_token = current_cache_tokens[0]
            for token in current_cache_tokens:
                user_claims = await self._authorize.get_raw_jwt(token)
                token_end = datetime.fromtimestamp(user_claims.get("exp"))
                if oldest > token_end:
                    oldest = token_end
                    oldest_token = token

            await self._cache.delete_tokens(user_uuid, oldest_token)

    async def __unset_tokens_from_cookies(
        self, access: bool = False, refresh: bool = False
    ) -> None:
        if access:
            await self._authorize.unset_access_cookies()
        if refresh:
            await self._authorize.unset_refresh_cookies()

    async def __set_tokens_to_cookies(self, tokens: CacheTokens) -> None:
        if tokens.access:
            await self._authorize.set_access_cookies(tokens.access)
        if tokens.refresh:
            await self._authorize.set_refresh_cookies(tokens.refresh)

    async def __create_tokens(self, user_claims: UserClaims) -> CacheTokens:
        new_access_token = await self._authorize.create_access_token(
            subject=user_claims.user_uuid, user_claims=user_claims.model_dump()
        )
        new_refresh_token = await self._authorize.create_refresh_token(
            subject=user_claims.user_uuid,
            expires_time=timedelta(settings.token_expire_time),
            user_claims=user_claims.model_dump(),
        )
        return CacheTokens(access=new_access_token, refresh=new_refresh_token)

    async def login(self, body: RequestLogin, request: Request):
        user = await self._user_repository.get_by_email(body.email)
        if not user:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="The email is not valid",
            )
        if not user.check_password(body.password.get_secret_value()):
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="Bad username or password",
            )
        user_data = UserClaims(
            user_uuid=str(user.uuid), role_uuid=str(user.role_uuid)
        )
        tokens = await self.__create_tokens(user_data)

        await self.__set_tokens_to_cookies(tokens)
        await self.__delete_oldest_token(user.uuid)
        await self._cache.set_token(user.uuid, tokens.refresh)

        await self._history_repository.create(
            RequestLoginHistory(
                user_uuid=user.uuid,
                ip_address=request.headers.get("Host"),
                user_agent=request.headers.get("User-Agent"),
            )
        )

    async def logout(self, request: Request, for_all_sessions: bool):
        refresh_token = request.cookies.get("refresh_token_cookie")
        if not refresh_token:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="No token",
            )
        raw_jwt = validate_token(refresh_token)

        await self._cache.delete_tokens(
            raw_jwt.get("user_uuid"),
            refresh_token,
            all=for_all_sessions,
        )
        await self.__unset_tokens_from_cookies(access=True, refresh=True)

    async def refresh(self, request: Request):
        token = request.cookies.get("refresh_token_cookie")
        if not token:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="No token",
            )
        raw_jwt = validate_token(token)
        tokens = await self._cache.get_tokens(raw_jwt.get("user_uuid"))
        if not tokens:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="Fake token",
            )
        current_refresh_tokens = [
            str(token, encoding=("utf-8")) for token in tokens
        ]
        if token not in current_refresh_tokens:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="Fake token",
            )

        user_data = UserClaims(
            user_uuid=raw_jwt.get("user_uuid"),
            role_uuid=raw_jwt.get("role_uuid"),
        )
        tokens = await self.__create_tokens(user_data)

        await self.__set_tokens_to_cookies(tokens)
        await self._cache.delete_tokens(user_data.user_uuid, token)
        await self._cache.set_token(user_data.user_uuid, tokens.refresh)

    @staticmethod
    def verify(request: Request):
        token = request.cookies.get("access_token_cookie")
        if not token:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="No token",
            )
        validate_token(token)


@lru_cache
def get_token_service(
    cache: RedisCache = Depends(get_redis),
    user_repository: UserRepository = Depends(get_user_repository),
    history_repository: LoginHistoryRepository = Depends(
        get_login_history_repository
    ),
    authorize: AuthJWT = Depends(auth_dep),
) -> TokenService:
    return TokenService(cache, user_repository, history_repository, authorize)
