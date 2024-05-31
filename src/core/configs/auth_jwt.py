from async_fastapi_jwt_auth import AuthJWT
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv(".env")


class AuthJWTSettings(BaseSettings):
    authjwt_secret_key: str = Field(..., alias="AUTHJWT_SECRET_KEY")
    authjwt_token_location: set = {"cookies"}
    authjwt_cookie_csrf_protect: bool = (
        Field(..., alias="AUTHJWT_COOKIE_CSRF_PROTECT") == "True"
    )
    authjwt_cookie_secure: bool = (
        Field(..., alias="AUTHJWT_COOKIE_SECURE") == "True"
    )


@AuthJWT.load_config
def get_config():
    return AuthJWTSettings()
