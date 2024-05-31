from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request
from fastapi_limiter.depends import RateLimiter

from src.auth.models.api.base import StringRepresent
from src.auth.models.api.v1.tokens import RequestLogin
from src.auth.models.api.v1.users import ResponseUser
from src.auth.services.token import TokenService, get_token_service

router = APIRouter()


@router.post(
    "/login/",
    response_model=ResponseUser,
    summary="Issuing a JWT token",
    dependencies=[Depends(RateLimiter(times=5, seconds=1))],
)
async def login(
    request: Request,
    body: RequestLogin,
    token_service: TokenService = Depends(get_token_service),
) -> ResponseUser:
    """Endpoint to receive JWT

    Issuing a JWT token

    Returns:
    - **StringRepresent**: Status code with message "The login was completed successfully"
    """
    return await token_service.login(body, request)


@router.post(
    "/logout/", response_model=StringRepresent, summary="Removing a JWT token"
)
async def logout(
    for_all_sessions: Annotated[
        bool | int,
        Query(
            title="For all sessions",
            description="The boolean to logout all sessions",
            example="False",
        ),
    ],
    request: Request,
    token_service: TokenService = Depends(get_token_service),
) -> StringRepresent:
    """Endpoint to delete the token (for_all_sessions=true to delete all sessions)

    Removing a JWT token

    Returns:
    - **StringRepresent**: Status code with message "RefreshToken has been deleted,
                            expired or does not exist"
    """
    if isinstance(for_all_sessions, int):
        for_all_sessions = bool(for_all_sessions)
    await token_service.logout(request, for_all_sessions)
    return StringRepresent(
        code=HTTPStatus.OK,
        details="RefreshToken has been deleted, expired or does not exist",
    )


@router.post(
    "/refresh/",
    response_model=StringRepresent,
    summary="JWT refresh",
    dependencies=[Depends(RateLimiter(times=5, seconds=1))],
)
async def refresh_token(
    request: Request,
    token_service: TokenService = Depends(get_token_service),
) -> StringRepresent:
    """Endpoint to refresh JWT

    JWT refresh

    Returns:
    - **StringRepresent**: Status code with message "The refresh was completed successfully"
    """
    await token_service.refresh(request)
    return StringRepresent(
        code=HTTPStatus.OK, details="The refresh was completed successfully"
    )


@router.post(
    "/verify/",
    response_model=StringRepresent,
    summary="verify access token",
    dependencies=[Depends(RateLimiter(times=5, seconds=1))],
)
async def verify_token(
    request: Request,
    token_service: TokenService = Depends(get_token_service),
) -> StringRepresent:
    """Endpoint to verify token

    Verify access token

    Returns:
    - **StringRepresent**: Status code with message "The token is valid"
    """
    token_service.verify(request)
    return StringRepresent(code=HTTPStatus.OK, details="The token is valid")
