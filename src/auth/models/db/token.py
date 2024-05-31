from pydantic import BaseModel


class CacheTokens(BaseModel):
    access: str
    refresh: str


class UserClaims(BaseModel):
    user_uuid: str
    role_uuid: str
