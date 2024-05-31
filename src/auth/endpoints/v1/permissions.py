from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Request

from src.auth.models.api.base import StringRepresent
from src.auth.models.api.v1.permissions import (
    RequestPermissionCreate,
    RequestPermissionUpdate,
    ResponsePermission,
    ResponsePermissionShort,
)
from src.auth.services.current_user import CurrentUserService, get_current_user
from src.auth.services.permission import (
    PermissionService,
    get_permission_service,
)
from src.auth.validators.permission import (
    PermissionValidator,
    get_permission_validator,
    permission_uuid_annotation,
)

router = APIRouter()


@router.get(
    "/",
    response_model=list[ResponsePermissionShort],
    summary="Get a list of permissions",
)
async def get_permissions(
    request: Request,
    permission_service: PermissionService = Depends(get_permission_service),
    current_user: CurrentUserService = Depends(get_current_user),
) -> list[ResponsePermissionShort]:
    """Only available to administrator

    Get a list of permissions

    Returns:
    - **list[ResponsePermission]**: The list of permission
    """
    await current_user.is_superuser(request)
    permissions = await permission_service.get_all()
    if not permissions:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="permissions not found"
        )
    return [
        ResponsePermissionShort(
            uuid=permission.uuid,
            name=permission.name,
        )
        for permission in permissions
    ]


@router.get(
    "/{permission_uuid}/",
    response_model=ResponsePermission,
    response_model_exclude_none=True,
    summary="Get a permission details by uuid",
)
async def get_permission(
    request: Request,
    permission_uuid: permission_uuid_annotation,
    permission_service: PermissionService = Depends(get_permission_service),
    current_user: CurrentUserService = Depends(get_current_user),
) -> ResponsePermission:
    """Only available to administrator

    Get a permission details by uuid

    Args:
    - **permission_uuid** (UUID): The UUID of the permission to get

    Returns:
    - **PermissionDB**: The permission details
    """
    await current_user.is_superuser(request)
    permission = await permission_service.get(permission_uuid)
    if not permission:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="permission not found"
        )
    return permission


@router.post(
    "/",
    response_model=ResponsePermission,
    response_model_exclude_none=True,
    summary="Create a permission",
)
async def create_permission(
    request: Request,
    body: RequestPermissionCreate,
    permission_service: PermissionService = Depends(get_permission_service),
    permission_validator: PermissionValidator = Depends(
        get_permission_validator
    ),
    current_user: CurrentUserService = Depends(get_current_user),
) -> ResponsePermission:
    """Only available to administrator

    Create a permission

    Returns:
    - **PermissionDB**: The permission details

    """
    await current_user.is_superuser(request)
    await permission_validator.is_duplicate_name(body.name)
    permission = await permission_service.create(body)
    return permission


@router.patch(
    "/{permission_uuid}/",
    response_model=ResponsePermission,
    response_model_exclude_none=True,
    summary="Change the permission by uuid",
)
async def update_permission(
    request: Request,
    permission_uuid: permission_uuid_annotation,
    body: RequestPermissionUpdate,
    permission_service: PermissionService = Depends(get_permission_service),
    permission_validator: PermissionValidator = Depends(
        get_permission_validator
    ),
    current_user: CurrentUserService = Depends(get_current_user),
) -> ResponsePermission:
    """Only available to administrator

    Change the permission by uuid

    Args:
    - **permission_uuid** (UUID): The UUID of the permission to change

    Returns:
    - **PermissionDB**: The permission details
    """
    await current_user.is_superuser(request)
    permission = await permission_service.update(
        await permission_validator.is_exists(permission_uuid), body
    )
    return permission


@router.delete(
    "/{permission_uuid}/",
    response_model=StringRepresent,
    summary="Delete the permission by uuid",
)
async def remove_permission(
    request: Request,
    permission_uuid: permission_uuid_annotation,
    permission_service: PermissionService = Depends(get_permission_service),
    permission_validator: PermissionValidator = Depends(
        get_permission_validator
    ),
    current_user: CurrentUserService = Depends(get_current_user),
) -> StringRepresent:
    """Only available to administrator

    Delete the permission by uuid

    Args:
    - **permission_uuid** (UUID): The UUID of the permission to delete

    Returns:
    - **StringRepresent**: Status code with message "Permission deleted successfully"
    """
    await current_user.is_superuser(request)
    await permission_service.remove(
        await permission_validator.is_exists(permission_uuid)
    )
    return StringRepresent(
        code=HTTPStatus.OK, details="Permission deleted successfully"
    )
