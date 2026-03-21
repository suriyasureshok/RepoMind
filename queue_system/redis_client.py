# queue_system/redis_client.py
import redis.asyncio as redis

from core.config import settings 


class RedisClient:
    _client = None

    @classmethod
    def get_client(cls):
        if cls._client is None:
            cls._client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True
            )
        return cls._client
