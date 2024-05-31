from functools import lru_cache
from http import HTTPStatus

from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.auth_jwt import AuthJWTBearer
from fastapi import Depends, HTTPException, Request

from src.auth.cache.redis import RedisCache, get_redis
from src.auth.models.api.v1.login_history import RequestLoginHistory
from src.auth.models.api.v1.tokens import RequestLogin
from src.auth.models.api.v1.users import ResponseUser
from src.auth.models.db.token import UserClaims
from src.auth.utils.tokens import TokenUtils, get_token
from src.auth.validators.token import validate_token
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
        token: TokenUtils,
    ):
        self._cache = cache
        self._user_repository = user_repository
        self._history_repository = history_repository
        self._authorize = authorize
        self._token = token

    async def login(self, body: RequestLogin, request: Request) -> ResponseUser:
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
        tokens = await self._token.create_tokens(user_data)

        await self._token.set_tokens_to_cookies(tokens)
        await self._token.delete_oldest_token(user.uuid)
        await self._cache.set_token(user.uuid, tokens.refresh)

        await self._history_repository.create(
            RequestLoginHistory(
                user_uuid=user.uuid,
                ip_address=request.headers.get("Host"),
                user_agent=request.headers.get("User-Agent"),
            )
        )
        model = ResponseUser.model_validate(user, from_attributes=True)
        return model

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
        await self._token.unset_tokens_from_cookies(access=True, refresh=True)

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
        tokens = await self._token.create_tokens(user_data)

        await self._token.set_tokens_to_cookies(tokens)
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
    token: TokenUtils = Depends(get_token),
) -> TokenService:
    return TokenService(
        cache, user_repository, history_repository, authorize, token
    )
