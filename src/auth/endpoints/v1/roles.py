from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Request

from src.auth.models.api.base import StringRepresent
from src.auth.models.api.v1.role_pemission import (
    RequestRolePermissionShortCreate,
)
from src.auth.models.api.v1.roles import (
    RequestRoleCreate,
    RequestRoleUpdate,
    ResponseRole,
    ResponseRoleExtended,
    ResponseRoleShort,
)
from src.auth.services.current_user import CurrentUserService, get_current_user
from src.auth.services.role import RoleService, get_role_service
from src.auth.services.role_pemission import (
    RolePermissionService,
    get_role_permission_service,
)
from src.auth.validators.permission import (
    PermissionValidator,
    get_permission_validator,
    permission_uuid_annotation,
)
from src.auth.validators.role import (
    RoleValidator,
    get_role_validator,
    role_uuid_annotation,
)
from src.auth.validators.role_permission import (
    RolePermissionValidator,
    get_role_permission_validator,
)

router = APIRouter()


@router.get(
    "/",
    response_model=list[ResponseRoleShort],
    summary="Get a list of roles",
)
async def get_roles(
    request: Request,
    roles_service: RoleService = Depends(get_role_service),
    current_user: CurrentUserService = Depends(get_current_user),
) -> list[ResponseRoleShort]:
    """Only available to administrator

    Get a list of roles

    Returns:
    - **list[ResponseRoleShort]**: The list of roles
    """
    await current_user.is_superuser(request)
    roles = await roles_service.get_all()
    if not roles:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="roles not found"
        )
    return [
        ResponseRoleShort(
            uuid=role.uuid,
            name=role.name,
        )
        for role in roles
    ]


@router.get(
    "/{role_uuid}/",
    response_model=ResponseRole,
    response_model_exclude_none=True,
    summary="Get a role details by uuid",
)
async def get_role(
    request: Request,
    role_uuid: role_uuid_annotation,
    roles_service: RoleService = Depends(get_role_service),
    current_user: CurrentUserService = Depends(get_current_user),
) -> ResponseRole:
    """Only available to administrator

    Get a role details by uuid

    Args:
    - **role_uuid** (str): The UUID of the role to get

    Returns:
    - **ResponseRole**: The role details
    """
    await current_user.is_superuser(request)
    role = await roles_service.get(role_uuid)
    if not role:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="permission not found"
        )
    return role


@router.post(
    "/",
    response_model=ResponseRole,
    response_model_exclude_none=True,
    summary="Create a role",
)
async def create_role(
    request: Request,
    body: RequestRoleCreate,
    roles_service: RoleService = Depends(get_role_service),
    role_validator: RoleValidator = Depends(get_role_validator),
    current_user: CurrentUserService = Depends(get_current_user),
) -> ResponseRole:
    """Only available to administrator

    Create a role

    Returns:
    - **ResponseRole**: The role details
    """
    await current_user.is_superuser(request)
    await role_validator.is_duplicate_name(body.name)
    role = await roles_service.create(body)
    return role


@router.patch(
    "/{role_uuid}/",
    response_model=ResponseRole,
    response_model_exclude_none=True,
    summary="Change the role by uuid",
)
async def update_role(
    request: Request,
    role_uuid: role_uuid_annotation,
    body: RequestRoleUpdate,
    roles_service: RoleService = Depends(get_role_service),
    role_validator: RoleValidator = Depends(get_role_validator),
    current_user: CurrentUserService = Depends(get_current_user),
) -> ResponseRole:
    """Only available to administrator

    Change the role by uuid

    Args:
    - **role_uuid** (str): The UUID of the role to change

    Returns:
    - **ResponseRole**: The role details
    """
    await current_user.is_superuser(request)
    role = await roles_service.update(
        await role_validator.is_exists(role_uuid), body
    )
    return role


@router.delete(
    "/{role_uuid}/",
    response_model=StringRepresent,
    summary="Delete the role by uuid",
)
async def remove_role(
    request: Request,
    role_uuid: role_uuid_annotation,
    roles_service: RoleService = Depends(get_role_service),
    role_validator: RoleValidator = Depends(get_role_validator),
    current_user: CurrentUserService = Depends(get_current_user),
) -> StringRepresent:
    """Only available to administrator

    Delete the role by uuid

    Args:
    - **role_uuid** (str): The UUID of the role to delete

    Returns:
    - **StringRepresent**: Status code with message "Role deleted successfully"
    """
    await current_user.is_superuser(request)
    await roles_service.remove(await role_validator.is_exists(role_uuid))
    return StringRepresent(
        code=HTTPStatus.OK, details="Role deleted successfully"
    )


@router.get(
    "/{role_uuid}/permissions/",
    response_model=ResponseRoleExtended,
    summary="Get all permission for role",
)
async def give_permissions_for_role(
    request: Request,
    role_uuid: role_uuid_annotation,
    role_permission_service: RolePermissionService = Depends(
        get_role_permission_service
    ),
    current_user: CurrentUserService = Depends(get_current_user),
) -> ResponseRoleExtended:
    """Available to authorized users

    Get a role details by uuid with permissions

    Args:
    - **role_uuid** (str): The UUID of the role to get

    Returns:
    - **ResponseRoleExtended**: The role details with permissions
    """
    await current_user.get_me(request)
    role = await role_permission_service.get_permissions_for_role(role_uuid)
    if not role:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Role not found"
        )
    return role


@router.post(
    "/{role_uuid}/permissions/{permission_uuid}/",
    response_model=ResponseRoleExtended,
    summary="Add permission for role",
)
async def add_permission_to_role(
    request: Request,
    role_uuid: role_uuid_annotation,
    permission_uuid: permission_uuid_annotation,
    role_permission_service: RolePermissionService = Depends(
        get_role_permission_service
    ),
    role_validator: RoleValidator = Depends(get_role_validator),
    permission_validator: PermissionValidator = Depends(
        get_permission_validator
    ),
    role_permission_validator: RolePermissionValidator = Depends(
        get_role_permission_validator
    ),
    current_user: CurrentUserService = Depends(get_current_user),
) -> ResponseRoleExtended:
    """Only available to administrator

    Add a permission for a role

    Args:
    - **role_uuid** (str): The UUID of the role
    - **permission_uuid** (str): The UUID of the permission for role

    Returns:
    - **ResponseRoleExtended**: The role details
    """
    await current_user.is_superuser(request)
    role_uuid = await role_validator.is_exists(role_uuid)
    permission_uuid = await permission_validator.is_exists(permission_uuid)
    body = RequestRolePermissionShortCreate(
        role_uuid=role_uuid,
        permission_uuid=permission_uuid,
    )
    await role_permission_validator.is_duplicate_row(
        body.role_uuid, body.permission_uuid
    )
    role = await role_permission_service.create_permission_for_role(body)
    return role


@router.delete(
    "/{role_uuid}/permissions/{permission_uuid}/",
    response_model=StringRepresent,
    summary="Delete permission for role",
)
async def remove_permission_from_role(
    request: Request,
    role_uuid: role_uuid_annotation,
    permission_uuid: permission_uuid_annotation,
    role_permission_service: RolePermissionService = Depends(
        get_role_permission_service
    ),
    role_validator: RoleValidator = Depends(get_role_validator),
    permission_validator: PermissionValidator = Depends(
        get_permission_validator
    ),
    current_user: CurrentUserService = Depends(get_current_user),
) -> StringRepresent:
    """Only available to administrator

    Remove permission for a role

    Args:
    - **role_uuid** (str): The UUID of the role to delete permission
    - **permission_uuid** (str): The UUID of the role permission to delete

    Returns:
    - **StringRepresent**: Status code with message "Permission for role deleted successfully"
    """
    await current_user.is_superuser(request)
    role_uuid = await role_validator.is_exists(role_uuid)
    permission_uuid = await permission_validator.is_exists(permission_uuid)
    await role_permission_service.remove_permission_for_role(
        role_uuid, permission_uuid
    )
    return StringRepresent(
        code=HTTPStatus.OK, details="Permission for role deleted successfully"
    )
