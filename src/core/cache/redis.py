from logging import Logger
from typing import Any

from redis.asyncio import Redis


class RedisBase:
    _redis: Redis
    _logger: Logger

    def __init__(self, redis: Redis, logger: Logger):
        self._redis = redis
        self._logger = logger

    async def close(self) -> None:
        """
        Закрыть соединение с Redis.
        """
        await self._redis.aclose()
        self._logger.info("Connection to Redis was closed.")

    async def ping(self) -> Any:
        """
        Ping the Redis server to ensure the connection is still alive.
        """
        return await self._redis.ping()
