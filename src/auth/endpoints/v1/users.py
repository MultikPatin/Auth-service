from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi_limiter.depends import RateLimiter

from src.auth.models.api.base import StringRepresent
from src.auth.models.api.v1.users import (
    RequestUserCreate,
    RequestUserUpdate,
    ResponseUser,
    ResponseUserShort,
)
from src.auth.services.current_user import CurrentUserService, get_current_user
from src.auth.services.user import UserService, get_user_service
from src.auth.validators.user import (
    UserValidator,
    get_user_validator,
    user_uuid_annotation,
)

router = APIRouter()


@router.get(
    "/", response_model=list[ResponseUserShort], summary="Get a list of users"
)
async def get_users(
    request: Request,
    current_user: CurrentUserService = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
) -> list[ResponseUserShort]:
    """Only available to administrator

    Get a list of users

    Returns:
    - **list[ResponseUserShort]**: The list of users
    """
    await current_user.is_superuser(request)
    users = await user_service.get_all()
    if not users:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="users not found"
        )
    return [
        ResponseUserShort(
            uuid=user.uuid,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
        )
        for user in users
    ]


@router.post(
    "/",
    response_model=ResponseUser,
    summary="Register the user",
    dependencies=[Depends(RateLimiter(times=5, seconds=1))],
)
async def create_user(
    body: RequestUserCreate,
    user_service: UserService = Depends(get_user_service),
    user_validator: UserValidator = Depends(get_user_validator),
) -> ResponseUser:
    """Register the user

    Returns:
    - **ResponseUser**: User details
    """
    await user_validator.is_duplicate_email(body.email)
    user = await user_service.create(body)
    return user


@router.get(
    "/me/",
    response_model=ResponseUser,
    summary="Get the user himself details by id",
    dependencies=[Depends(RateLimiter(times=5, seconds=1))],
)
async def get_user_me(
    request: Request,
    current_user: CurrentUserService = Depends(get_current_user),
) -> ResponseUser:
    """Get the user himself details

    Returns:
    - **ResponseUser**: User details
    """
    return await current_user.get_me(request)


@router.get(
    "/{user_uuid}/",
    response_model=ResponseUser,
    summary="Get user details by uuid",
)
async def get_user(
    request: Request,
    user_uuid: user_uuid_annotation,
    user_service: UserService = Depends(get_user_service),
    current_user: CurrentUserService = Depends(get_current_user),
) -> ResponseUser:
    """Only available to administrator

    Get user details by uuid

    Args:
    - **user_uuid** (str): The UUID of the user to get

    Returns:
    - **ResponseUser**: User details
    """
    await current_user.is_superuser(request)
    user = await user_service.get(user_uuid)
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="user not found"
        )
    return user


@router.patch(
    "/{user_uuid}/",
    response_model=ResponseUser,
    summary="Change information about the user by uuid",
)
async def update_user(
    request: Request,
    user_uuid: user_uuid_annotation,
    body: RequestUserUpdate,
    user_service: UserService = Depends(get_user_service),
    user_validator: UserValidator = Depends(get_user_validator),
    current_user: CurrentUserService = Depends(get_current_user),
) -> ResponseUser:
    """Only available to administrator

    Change information about the user by uuid

    Args:
    - **user_uuid** (str): The UUID of the user to change

    Returns:
    - **ResponseUser**: User details
    """
    await current_user.is_superuser(request)
    user = await user_service.update(
        await user_validator.is_exists(user_uuid), body
    )
    return user


@router.delete(
    "/{user_uuid}/",
    response_model=StringRepresent,
    summary="Delete user by uuid",
)
async def remove_user(
    request: Request,
    user_uuid: user_uuid_annotation,
    user_service: UserService = Depends(get_user_service),
    user_validator: UserValidator = Depends(get_user_validator),
    current_user: CurrentUserService = Depends(get_current_user),
) -> StringRepresent:
    """Only available to administrator

    Delete user by uuid

    Args:
    - **user_uuid** (str): The UUID of the user to delete

    Returns:
    - **StringRepresent**: Status code with message "User deleted successfully"
    """
    await current_user.is_superuser(request)
    await user_service.remove(await user_validator.is_exists(user_uuid))
    return StringRepresent(
        code=HTTPStatus.OK, details="User deleted successfully"
    )
