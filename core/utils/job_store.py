# core/utils/job_store.py

import asyncio

from queue_system.redis_client import RedisClient
from .exceptions import JobStoreError


class JobStore:

    def __init__(self):
        self.redis = RedisClient.get_client()

    async def set_status(self, job_id: str, status: str):
        try:
            await self.redis.set(f"job:{job_id}:status", status)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            raise JobStoreError(f"Failed to set status for job {job_id}: {exc}") from exc

    async def get_status(self, job_id: str) -> str | None:
        try:
            return await self.redis.get(f"job:{job_id}:status")
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            raise JobStoreError(f"Failed to get status for job {job_id}: {exc}") from exc
