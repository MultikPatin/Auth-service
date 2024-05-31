import logging
from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from authlib.integrations.httpx_client import AsyncOAuth2Client
from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter
from redis.asyncio import Redis

from src.auth.cache import redis
from src.auth.core.config import PostgresAuthConnect, settings
from src.auth.core.logger import LOGGING
from src.auth.endpoints.v1 import (
    oauth2,
    permissions,
    roles,
    tokens,
    users,
    users_additional,
)
from src.auth.oauth_clients import google
from src.auth.utils.startup import StartUpService
from src.core.db.clients.postgres import PostgresDatabase
from src.core.utils.logger import create_logger


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    startup_methods: StartUpService = StartUpService(
        PostgresDatabase(PostgresAuthConnect()),
    )
    await startup_methods.create_partition()
    await startup_methods.create_empty_role()
    await startup_methods.create_admin_user()
    redis.redis = redis.RedisCache(
        Redis(**settings.redis.connection_dict),
        logger=create_logger("API RedisCache"),
    )
    google.google = google.OauthGoogle(
        AsyncOAuth2Client(**settings.google.settings_dict),
        logger=create_logger("API OAUTH Google"),
    )
    settings.redis.correct_port()
    redis_limiter_connection = Redis(**settings.redis.connection_dict)
    await FastAPILimiter.init(redis_limiter_connection)
    yield
    await redis.redis.close()
    await FastAPILimiter.close()


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
app.include_router(oauth2.router, prefix="/auth/v1/oauth2", tags=["oauth2"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
