from typing import Annotated
from uuid import UUID

from fastapi import Depends, Path

from src.auth.validators.base import BaseValidator, DuplicateNameValidatorMixin
from src.core.db.entities import Permission
from src.core.db.repositories.permission import (
    PermissionRepository,
    get_permission_repository,
)


class PermissionValidator(
    BaseValidator[PermissionRepository, Permission], DuplicateNameValidatorMixin
):
    pass


def get_permission_validator(
    repository: PermissionRepository = Depends(get_permission_repository),
) -> PermissionValidator:
    return PermissionValidator(repository)


permission_uuid_annotation = Annotated[
    UUID,
    Path(
        alias="permission_uuid",
        title="permission uuid",
        description="The UUID of the permission",
        example="6a0a479b-cfec-41ac-b520-41b2b007b611",
    ),
]
