from http import HTTPStatus

from fastapi import HTTPException
from jwt import (
    ExpiredSignatureError,
    InvalidSignatureError,
    decode,
)

from src.auth.core.config import settings


def validate_token(token) -> dict[str, str] | None:
    try:
        raw_jwt = decode(
            token,
            key=settings.authjwt_secret_key,
            algorithms=settings.authjwt_algorithm,
        )
    except (InvalidSignatureError, ExpiredSignatureError) as e:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail=f"{e}: invalid token",
        ) from None
    return raw_jwt
