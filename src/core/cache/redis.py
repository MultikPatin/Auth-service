from logging import Logger
from typing import Any
from uuid import UUID

from redis.asyncio import Redis

from src.api.core.config import settings
from src.core.cache.abstract import AbstractModelCache


class RedisCache(AbstractModelCache):
    """
    Клиент для работы api с Redis.

    Args:
        redis (Redis): объект для работы с Redis
        logger (Logger): объект для записи в журналы

    """

    __redis: Redis
    __logger: Logger

    def __init__(self, redis: Redis, logger: Logger):
        self.__redis = redis
        self.__logger = logger

    async def _collect_keys(self, pattern: UUID | str) -> list[str] | None:
        """
        Собрать все refresh_tokens пользователя.

        Args:
            pattern (UUID | str): паттерн для поиска ключей.

        Returns:
            list[str] | None: возвращает валидные ключи.

        """
        max_sessions = settings.user_max_sessions
        keys = []
        async for key in self.__redis.scan_iter(f"{str(pattern)}:*", 10000):
            keys.append(key)
            if len(keys) == max_sessions:
                break
        return keys

    async def _build_key(self, prefix: UUID | str, token: bytes | str) -> str:
        """
        Сформировать ключ для Redis.

        Args:
            prefix (UUID | str): префикс ключа.
            token (bytes | str): тело ключа.

        Returns:
            str : возвращает ключ.

        """
        if isinstance(token, bytes):
            token = str(token, encoding="utf-8")
        return f"{str(prefix)}:{token}"

    async def set_token(
        self,
        uuid: str | UUID,
        token: str | bytes,
    ) -> None:
        """
        Записать токены в кэш Redis.

        Args:
            uuid (str | UUID): user_uuid для формирования ключа (prefix).
            token (str | bytes): токен для формирования ключа (тело); значение ключа.

        """

        key = await self._build_key(uuid, token)
        value = token
        token_expire_in_days = settings.token_expire_time
        token_expire_in_sec = token_expire_in_days * 24 * 60 * 60

        try:
            await self.__redis.set(key, value, token_expire_in_sec)
        except Exception as set_error:
            self.__logger.error(
                "Error setting value with key `%s::%s`: %s.",
                key,
                value,
                set_error,
            )
            raise

    async def get_tokens(
        self,
        key_pattern: UUID | str,
    ) -> list[bytes] | None:
        """
        Получить токены из кэша Redis.

        Args:
            key_pattern (str): аргумент для паттерн ключа для получения токенов.

        Returns:
            list | None: возвращает список токенов или None, если токены не найдены.

        """
        keys = await self._collect_keys(key_pattern)

        try:
            values = await self.__redis.mget(keys)
            if not values:
                return None
        except Exception as get_error:
            self.__logger.error(
                "Error getting value with key `%s`: %s.", key_pattern, get_error
            )
            raise

        return values

    async def delete_tokens(
        self, uuid: UUID | str, token: bytes | str, all: bool = False
    ) -> None:
        """
        Удалить токены из кэша Redis.

        Args:
            uuid (UUID | str): Паттерн для ключ для удаления токенов; префикс для ключа.
            token (bytes | str): Тело для формирования ключа для удаления.
            all (bool) Параметр для переключения между одиночным и множественным удалением.

        """
        if all:
            key_pattern = uuid
            keys = await self._collect_keys(key_pattern)
        else:
            key = await self._build_key(uuid, token)
            keys = [key]
        try:
            await self.__redis.delete(*keys)
        except Exception as get_error:
            self.__logger.error(
                "Error deletion value with key `%s`: %s.", key, get_error
            )
            raise
        return

    async def close(self) -> None:
        """
        Закрыть соединение с Redis.

        """
        await self.__redis.aclose()
        self.__logger.info("Connection to Redis was closed.")

    async def ping(self) -> Any:
        """
        Ping the Redis server to ensure the connection is still alive.

        Returns:
            bool: True if the ping was successful, False if it failed.
        """
        return await self.__redis.ping()


redis: RedisCache | None = None


async def get_redis() -> RedisCache | None:
    return redis
