# queue_system/redis_client.py

import redis.asyncio as redis

from core.config import settings
from core.logging import logger


class RedisClient:
    _client = None

    @classmethod
    def get_client(cls):
        if cls._client is None:
            cls._client = redis.from_url(settings.REDIS_URL, decode_responses=True)
            logger.info("Redis client initialized")
            return cls._client

    @classmethod
    async def close_client(cls):
        if cls._client is None:
            return

        try:
            await cls._client.aclose()
            logger.info("Redis client closed")
        except Exception as exc:
            logger.error(f"Error while closing Redis client: {exc}")
        finally:
            cls._client = None
