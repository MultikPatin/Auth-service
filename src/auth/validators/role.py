from typing import Annotated
from uuid import UUID

from fastapi import Depends, Path

from src.auth.validators.base import BaseValidator, DuplicateNameValidatorMixin
from src.core.db.entities import Role
from src.core.db.repositories.role import RoleRepository, get_role_repository


class RoleValidator(
    BaseValidator[RoleRepository, Role], DuplicateNameValidatorMixin
):
    pass


def get_role_validator(
    repository: RoleRepository = Depends(get_role_repository),
) -> RoleValidator:
    return RoleValidator(repository)


role_uuid_annotation = Annotated[
    UUID,
    Path(
        alias="role_uuid",
        title="role uuid",
        description="The UUID of the role",
        example="6a0a479b-cfec-41ac-b520-41b2b007b611",
    ),
]
