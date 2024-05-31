from uuid import UUID

from sqlalchemy import select, text

from src.auth.core.config import settings
from src.auth.models.api.v1.roles import RequestRoleCreate
from src.auth.models.api.v1.users import RequestUserCreate
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

    async def create_partition(self) -> None:
        """creating partition by login_history"""
        async with self._database.get_session() as session:
            await session.execute(
                text(
                    """CREATE SCHEMA IF NOT EXISTS partman;
                    """
                )
            )
            await session.execute(
                text(
                    """CREATE EXTENSION IF NOT EXISTS pg_partman WITH SCHEMA partman;
                    """
                )
            )
            await session.execute(
                text(
                    """DROP TABLE IF EXISTS public.login_history CASCADE ;
                    """
                )
            )
            await session.execute(
                text(
                    """DROP TABLE IF EXISTS public.login_history_template CASCADE ;
                    """
                )
            )
            await session.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS public.login_history (
                        user_uuid uuid NOT NULL,
                        ip_address VARCHAR(64) NOT NULL,
                        user_agent VARCHAR(255) NOT NULL,
                        uuid uuid NOT NULL,
                        created_at timestamp NOT NULL DEFAULT TIMEZONE('utc', now()),
                        updated_at timestamp NOT NULL DEFAULT TIMEZONE('utc', now())
                    ) PARTITION BY RANGE (created_at);
                    """
                )
            )
            await session.execute(
                text(
                    """
                    CREATE INDEX ON public.login_history (created_at);
                    """
                )
            )
            await session.execute(
                text(
                    """CREATE TABLE IF NOT EXISTS public.login_history_template (LIKE public.login_history);
                    """
                )
            )
            await session.execute(
                text(
                    """ALTER TABLE public.login_history_template ADD PRIMARY KEY (uuid);
                    """
                )
            )
            await session.execute(
                text(
                    """ALTER TABLE public.login_history_template ADD FOREIGN KEY (user_uuid) REFERENCES public.users (uuid);
                    """
                )
            )
            await session.execute(
                text(
                    """
                    TRUNCATE partman.part_config_sub CASCADE;
                    """
                )
            )
            await session.execute(
                text(
                    """
                    TRUNCATE partman.part_config CASCADE;
                    """
                )
            )
            await session.execute(
                text(
                    """
                    SELECT partman.create_parent(
                        p_parent_table := 'public.login_history',
                        p_control := 'created_at',
                        p_interval := '30 day',
                        p_template_table := 'public.login_history_template'
                    );
                    """
                )
            )
            await session.commit()
