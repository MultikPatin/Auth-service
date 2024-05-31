from http import HTTPStatus

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse, Response
from fastapi_limiter.depends import RateLimiter

from src.auth.models.api.base import StringRepresent
from src.auth.services.google_oauth2 import OAuth2Service, get_oauth2_service

router = APIRouter()


@router.get(
    "/oauth_google_login/",
    summary="Generate google oauth server authorization url and redirect there",
    dependencies=[Depends(RateLimiter(times=5, seconds=1))],
)
async def oauth_google_login(
    oauth2_service: OAuth2Service = Depends(get_oauth2_service),
) -> RedirectResponse:
    """Endpoint to get to oauth server

    Generate google oauth server authorization url and redirect there

    Returns:
    - **RedirectResponse**: Redirect to google oauth server
    """
    authorization_url = await oauth2_service.get_google_authorization_url()
    return RedirectResponse(url=authorization_url)


@router.get(
    "/google_auth/",
    response_model=StringRepresent,
    summary="Get user info from oauth server and login",
    dependencies=[Depends(RateLimiter(times=5, seconds=1))],
)
async def google_auth(
    request: Request,
    response: Response,
    oauth2_service: OAuth2Service = Depends(get_oauth2_service),
) -> StringRepresent:
    """User authentication in the google auth service

    Get user info from google oauth server and login

    Returns:
    - **StringRepresent**: Status code with message "The google login was completed successfully"
    """
    result = await oauth2_service.auth_via_google(request, response)
    user_data = await oauth2_service.checkin_oauth_user(result)
    await oauth2_service.login(request, user_data)
    return StringRepresent(
        code=HTTPStatus.OK,
        details="The google login was completed successfully",
    )
