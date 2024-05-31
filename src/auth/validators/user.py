from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Path

from src.auth.validators.base import BaseValidator
from src.core.db.entities import User
from src.core.db.repositories.user import UserRepository, get_user_repository


class UserValidator(BaseValidator[UserRepository, User]):
    async def is_duplicate_email(self, name: str) -> None:
        user_uuid = await self._repository.get_uuid_by_email(name)
        if user_uuid is not None:
            raise HTTPException(
                status_code=400,
                detail="An object with that email already exists",
            )


def get_user_validator(
    repository: UserRepository = Depends(get_user_repository),
) -> UserValidator:
    return UserValidator(repository)


user_uuid_annotation = Annotated[
    UUID,
    Path(
        alias="user_uuid",
        title="user uuid",
        description="The UUID of the user",
        example="6a0a479b-cfec-41ac-b520-41b2b007b611",
    ),
]
