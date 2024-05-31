from http import HTTPStatus
from typing import Any

from fastapi import HTTPException
from jwt import (
    ExpiredSignatureError,
    InvalidSignatureError,
    decode,
    get_unverified_header,
)

from src.api.core.config import settings


def validate_token(token) -> Any:
    header_data = get_unverified_header(token)
    try:
        raw_jwt = decode(
            token,
            key=settings.auth_jwt.authjwt_secret_key,
            algorithms=[
                header_data["alg"],
            ],
        )
    except (InvalidSignatureError, ExpiredSignatureError) as e:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail=f"{e}: invalid token",
        ) from None
    return raw_jwt
