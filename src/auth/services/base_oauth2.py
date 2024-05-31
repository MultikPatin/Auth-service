import random
import string

from async_fastapi_jwt_auth import AuthJWT
from fastapi import Request
from werkzeug.security import generate_password_hash

from src.auth.cache.redis import RedisCache
from src.auth.models.api.v1.login_history import RequestLoginHistory
from src.auth.models.api.v1.social_account import RequestSocialAccount
from src.auth.models.api.v1.users import RequestUserCreate
from src.auth.models.db.token import UserClaims
from src.auth.models.db.user import UserDB
from src.auth.utils.tokens import TokenUtils
from src.core.db.repositories.login_history import LoginHistoryRepository
from src.core.db.repositories.social_account import SocialAccountRepository
from src.core.db.repositories.user import UserRepository


class BaseService:
    def __init__(
        self,
        cache: RedisCache,
        user_repository: UserRepository,
        history_repository: LoginHistoryRepository,
        social_account_repository: SocialAccountRepository,
        authorize: AuthJWT,
        token: TokenUtils,
    ):
        self._cache = cache
        self._user_repository = user_repository
        self._history_repository = history_repository
        self._social_account_repository = social_account_repository
        self._authorize = authorize
        self._token = token

    async def checkin_oauth_user(
        self, data: UserClaims | dict[str, str]
    ) -> UserClaims:
        if isinstance(data, UserClaims):
            return data
        else:
            claims = data
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

    async def check_social_account(
        self, claims: dict[str, str]
    ) -> dict[str, str] | UserClaims:
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
