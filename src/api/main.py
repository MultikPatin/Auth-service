import logging
from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from fastapi import FastAPI
from redis.asyncio import Redis

from src.api.core.config import settings
from src.api.core.logger import LOGGING
from src.api.endpoints.v1 import (
    permissions,
    roles,
    tokens,
    users,
    users_additional,
)
from src.api.utils.startup import StartUpService
from src.core.cache import redis
from src.core.configs.postgres import PostgresSettings
from src.core.db.clients.postgres import PostgresDatabase
from src.core.utils.logger import create_logger


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    startup_methods: StartUpService = StartUpService(
        PostgresDatabase(PostgresSettings()),
    )
    await startup_methods.create_empty_role()
    await startup_methods.create_admin_user()
    redis.redis = redis.RedisCache(
        Redis(**settings.redis.connection_dict),
        logger=create_logger("API RedisCache"),
    )
    yield
    await redis.redis.close()


app = FastAPI(
    title=settings.name,
    description=settings.description,
    docs_url=settings.docs_url,
    openapi_url=settings.openapi_url,
    lifespan=lifespan,
)

app.include_router(
    users.router,
    prefix="/auth/v1/users",
    tags=["users"],
)
app.include_router(
    users_additional.router, prefix="/auth/v1/users", tags=["users_additional"]
)
app.include_router(
    permissions.router, prefix="/auth/v1/permissions", tags=["permissions"]
)
app.include_router(tokens.router, prefix="/auth/v1/tokens", tags=["tokens"])
app.include_router(roles.router, prefix="/auth/v1/roles", tags=["roles"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
