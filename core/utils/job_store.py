# core/utils/job_store.py

import asyncio
from typing import Iterable

from redis.exceptions import WatchError

from queue_system.redis_client import RedisClient

from .exceptions import JobNotCancellableError, JobNotFoundError, JobStoreError


class JobStore:

    def __init__(self):
        self.redis = RedisClient.get_client()

    async def set_status(self, job_id: str, status: str):
        try:
            await self.redis.set(f"job:{job_id}:status", status)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            raise JobStoreError(
                f"Failed to set status for job {job_id}: {exc}"
            ) from exc

    async def get_status(self, job_id: str) -> str | None:
        try:
            return await self.redis.get(f"job:{job_id}:status")
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            raise JobStoreError(
                f"Failed to get status for job {job_id}: {exc}"
            ) from exc

    async def cancel_if_cancellable(
        self,
        job_id: str,
        cancellable_states: Iterable[str] = ("PENDING", "RUNNING"),
        target_state: str = "CANCELLED",
    ) -> str:
        key = f"job:{job_id}:status"
        allowed_states = set(cancellable_states)

        try:
            async with self.redis.pipeline(transaction=True) as pipe:
                while True:
                    try:
                        await pipe.watch(key)
                        current_status = await pipe.get(key)

                        if current_status is None:
                            await pipe.reset()
                            raise JobNotFoundError(job_id)

                        if isinstance(current_status, bytes):
                            current_status = current_status.decode(
                                "utf-8", errors="replace"
                            )

                        if current_status not in allowed_states:
                            await pipe.reset()
                            raise JobNotCancellableError(job_id, str(current_status))

                        pipe.multi()
                        pipe.set(key, target_state)
                        await pipe.execute()
                        await pipe.reset()
                        return target_state
                    except WatchError:
                        continue
        except asyncio.CancelledError:
            raise
        except (JobNotFoundError, JobNotCancellableError):
            raise
        except Exception as exc:
            raise JobStoreError(f"Failed to cancel job {job_id}: {exc}") from exc
