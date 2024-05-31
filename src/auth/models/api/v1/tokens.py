from pydantic import BaseModel

from src.auth.models.api.base import LoginMixin, TokenMixin


class ResponseToken(BaseModel):
    refresh: str
    access: str


class RequestLogin(LoginMixin):
    pass


class RequestTokenRemover(TokenMixin):
    for_all_sessions: bool


class RequestTokenRefreshChecker(TokenMixin): ...


class RequestTokenVerify(TokenMixin):
    access: str
