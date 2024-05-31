import asyncio

import pytest
import pytest_asyncio

from tests.functional.settings import settings
import psycopg2

from redis.asyncio import Redis
import aiohttp


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
def postgres_client():
    client = psycopg2.connect(**settings.psycopg2_connect)
    yield client
    client.close()


@pytest_asyncio.fixture(scope="session")
async def redis_client():
    client = Redis(**settings.get_redis_host)
    yield client
    await client.aclose()


@pytest_asyncio.fixture(scope="session")
async def session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()
