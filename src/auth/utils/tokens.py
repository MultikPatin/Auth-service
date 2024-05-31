from datetime import datetime, timedelta
from functools import lru_cache
from uuid import UUID

from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.auth_jwt import AuthJWTBearer
from fastapi import Depends

from src.auth.cache.redis import RedisCache, get_redis
from src.auth.core.config import settings
from src.auth.models.db.token import CacheTokens, UserClaims
from src.core.db.repositories.login_history import (
    LoginHistoryRepository,
    get_login_history_repository,
)
from src.core.db.repositories.user import UserRepository, get_user_repository

auth_dep = AuthJWTBearer()


class TokenUtils:
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

    async def delete_oldest_token(self, user_uuid: UUID):
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

    async def unset_tokens_from_cookies(
        self, access: bool = False, refresh: bool = False
    ) -> None:
        if access:
            await self._authorize.unset_access_cookies()
        if refresh:
            await self._authorize.unset_refresh_cookies()

    async def set_tokens_to_cookies(self, tokens: CacheTokens) -> None:
        if tokens.access:
            await self._authorize.set_access_cookies(tokens.access)
        if tokens.refresh:
            await self._authorize.set_refresh_cookies(tokens.refresh)

    async def create_tokens(self, user_claims: UserClaims) -> CacheTokens:
        new_access_token = await self._authorize.create_access_token(
            subject=user_claims.user_uuid, user_claims=user_claims.model_dump()
        )
        new_refresh_token = await self._authorize.create_refresh_token(
            subject=user_claims.user_uuid,
            expires_time=timedelta(settings.token_expire_time),
            user_claims=user_claims.model_dump(),
        )
        return CacheTokens(access=new_access_token, refresh=new_refresh_token)


@lru_cache
def get_token(
    cache: RedisCache = Depends(get_redis),
    user_repository: UserRepository = Depends(get_user_repository),
    history_repository: LoginHistoryRepository = Depends(
        get_login_history_repository
    ),
    authorize: AuthJWT = Depends(auth_dep),
) -> TokenUtils:
    return TokenUtils(cache, user_repository, history_repository, authorize)
