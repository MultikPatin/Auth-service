import pytest

from redis.asyncio import Redis
from psycopg2.extensions import connection as _connection
from psycopg2.extras import execute_values
from tests.functional.settings import settings


@pytest.fixture
def transform_data():
    async def inner(data: list[dict]):
        return [[value for value in item.values()] for item in data]
    return inner

@pytest.fixture
def make_query():
    async def inner(table: str, columns: list[str]):
        write_query = f"""
            INSERT INTO public.{table} ({','.join(columns)}) VALUES %s
            ON CONFLICT (uuid) DO NOTHING;
        """
        return write_query
    return inner

@pytest.fixture
def postgres_write_data(postgres_client: _connection, transform_data, make_query: str):
    async def inner(data: list[dict], table: str):
        columns = data[0].keys()
        query = await make_query(table, columns)
        values = await transform_data(data)
        try:
            cursor = postgres_client.cursor()
            execute_values(cursor, query, values)
            postgres_client.commit()
        except Exception as e:
            postgres_client.rollback()
            raise e(f"Ошибка записи данных: {values} в Postgres")
        finally:
            if postgres_client:
                cursor.close()
    return inner


@pytest.fixture
def postgres_execute(postgres_client: _connection):
    async def inner(query: str):
        try:
            cursor = postgres_client.cursor()
            cursor.execute(query)
            postgres_client.commit()
        except Exception as e:
            postgres_client.rollback()
            raise e("Ошибка работы с данными в Postgres")
        finally:
            if postgres_client:
                cursor.close()
    return inner


@pytest.fixture
def clear_cache(redis_client: Redis):
    async def inner():
        await redis_client.flushdb(asynchronous=True)

    return inner

@pytest.fixture
def set_token(redis_client: Redis):
    async def inner(uuid, token):
        if isinstance(token, bytes):
            token = str(token, encoding="utf-8")
        key = f"{str(uuid)}:{token}"
        value = token
        token_expire_in_days = settings.token_expire_time
        token_expire_in_sec = token_expire_in_days * 24 * 60 * 60

        try:
            await redis_client.set(key, value, token_expire_in_sec)
        except Exception:
            raise Exception
    return inner


@pytest.fixture
def get_tokens(redis_client: Redis):
    async def inner(key_pattern):
        max_sessions = settings.user_max_sessions
        keys = []
        async for key in redis_client.scan_iter(f"{str(key_pattern)}:*", 10000):
            keys.append(key)
            if len(keys) == max_sessions:
                break
        try:
            values = await redis_client.mget(keys)
            if not values:
                return None
        except Exception:
            raise Exception
        return values
    return inner


@pytest.fixture
def delete_tokens(redis_client: Redis):
    async def inner(uuid, token, all=False):
        if all:
            key_pattern = uuid
            max_sessions = settings.user_max_sessions
            keys = []
            async for key in redis_client.scan_iter(f"{str(key_pattern)}:*", 10000):
                keys.append(key)
                if len(keys) == max_sessions:
                    break
        else:
            if isinstance(token, bytes):
                token = str(token, encoding="utf-8")
            key = f"{str(uuid)}:{token}"
            keys = [key]
        try:
            await redis_client.delete(*keys)
        except Exception:
            raise Exception
    return inner
