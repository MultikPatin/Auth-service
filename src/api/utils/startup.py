from uuid import UUID

from sqlalchemy import select

from src.api.core.config import settings
from src.api.models.api.v1.roles import RequestRoleCreate
from src.api.models.api.v1.users import RequestUserCreate
from src.core.db.clients.postgres import PostgresDatabase
from src.core.db.entities import Role, User


class StartUpService:
    def __init__(self, database: PostgresDatabase):
        self._database = database

    async def create_empty_role(self) -> None:
        body = RequestRoleCreate(
            name=settings.empty_role_name,
            description=settings.empty_role_description,
        )
        role_uuid = await self.get_uuid_by_name(body.name)
        if role_uuid is not None:
            return
        await self.create_role(body)

    async def create_admin_user(self) -> None:
        body = RequestUserCreate(
            email=settings.admin_email,
            password=settings.admin_password.get_secret_value(),
            first_name=None,
            last_name=None,
        )
        user_uuid = await self.get_uuid_by_email(body.email)
        if user_uuid is not None:
            return
        await self.create_user(body)

    async def get_uuid_by_name(self, name: str) -> UUID | None:
        async with self._database.get_session() as session:
            db_obj = await session.execute(
                select(Role.uuid).where(Role.name == name)
            )
            obj_uuid = db_obj.scalars().first()
            return obj_uuid

    async def get_uuid_by_email(self, email: str) -> UUID | None:
        async with self._database.get_session() as session:
            db_obj = await session.execute(
                select(User.uuid).where(User.email == email)
            )
            obj_uuid = db_obj.scalars().first()
            return obj_uuid

    async def create_role(self, instance: RequestRoleCreate) -> None:
        async with self._database.get_session() as session:
            db_obj = Role(**instance.dict())
            session.add(db_obj)
            await session.commit()

    async def create_user(self, instance: RequestUserCreate) -> None:
        async with self._database.get_session() as session:
            role_uuid = await self.get_uuid_by_name(settings.empty_role_name)
            instance_dict = instance.dict()
            instance_dict["is_superuser"] = True
            instance_dict["role_uuid"] = role_uuid
            db_obj = User(**instance_dict)
            session.add(db_obj)
            await session.commit()
