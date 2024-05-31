import pytest
import jwt
from tests.functional.settings import settings
from tests.functional.testdata.tokens_data import CacheTokens, UserClaims
from fastapi import HTTPException
from http import HTTPStatus


@pytest.fixture
def validate_token():
    async def inner(token: str | bytes):
        try:
            header_data = jwt.get_unverified_header(token)
            raw_jwt = jwt.decode(
                token,
                key=settings.secret_key,
                algorithms=[
                    header_data["alg"],
                ],
            )
        except Exception as e:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail=f"{e}: invalid token",
            ) from None
        return raw_jwt
    return inner


async def create_token(user_claims: UserClaims, token_type: str, secret_key: str):
    payload = user_claims.model_dump()
    payload.update({
                "sub": user_claims.user_uuid,
                'type': token_type
            })
    return jwt.encode(
            payload=payload,
            key=secret_key,
        )


@pytest.fixture
def create_tokens():
    async def inner(user_claims: UserClaims, secret_key: str = settings.secret_key) -> CacheTokens:
        new_access_token = await create_token(user_claims, "access", secret_key)
        new_refresh_token = await create_token(user_claims, "refresh", secret_key)
        return CacheTokens(access_token_cookie=new_access_token, refresh_token_cookie=new_refresh_token)
    return inner
