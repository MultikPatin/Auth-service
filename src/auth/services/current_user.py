from http import HTTPStatus

from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.auth_jwt import AuthJWTBearer
from fastapi import Depends, HTTPException, Request

from src.auth.models.api.v1.users import ResponseUser
from src.auth.validators.token import validate_token
from src.core.db.repositories.user import UserRepository, get_user_repository

auth_dep = AuthJWTBearer()


class CurrentUserService:
    def __init__(
        self,
        user_repository: UserRepository,
        authorize: AuthJWT,
    ):
        self._user_repository = user_repository
        self._authorize = authorize

    async def get_me(self, request: Request) -> ResponseUser:
        token = request.cookies.get("access_token_cookie")
        if not token:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="No token",
            )

        user_uuid = validate_token(token).get("user_uuid")
        if not user_uuid:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail="user not found"
            )
        obj = await self._user_repository.get(user_uuid)
        if not obj:
            return
        model = ResponseUser.model_validate(obj, from_attributes=True)
        return model

    async def is_superuser(self, request: Request):
        user = await self.get_me(request)
        if not user.is_superuser:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail="You do not have sufficient "
                "permissions to perform this action.",
            )


def get_current_user(
    user_repository: UserRepository = Depends(get_user_repository),
    authorize: AuthJWT = Depends(auth_dep),
) -> CurrentUserService:
    return CurrentUserService(user_repository, authorize)
