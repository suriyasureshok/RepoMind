# queue_system/queue_manager.py

import asyncio
from typing import Optional

from core.constants import (DEAD_LETTER_QUEUE, EMBEDDING_QUEUE,
                            EMBEDDING_QUEUE_MAX_SIZE)
from core.logging import logger
from core.utils.serializer import (serialize_task, deserialize_task)
from core.utils.exceptions import QueueError
from models import Task

from .redis_client import RedisClient


class QueueManager:

    def __init__(self):
        self.redis = RedisClient.get_client()
        logger.info("QueueManager initialized")

    # Push task to queue
    async def push_task(self, queue_name: str, task: Task):
        task_str = serialize_task(task)

        try:
            await self.redis.rpush(queue_name, task_str)
            logger.info(f"Task {task.task_id} pushed to {queue_name}")
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            raise QueueError(
                f"Failed to push task {task.task_id} to {queue_name}: {exc}"
            ) from exc

    # Pop task (blocking)
    async def pop_task(self, queue_name: str) -> Optional[Task]:
        try:
            result = await self.redis.blpop(queue_name, timeout=5)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            raise QueueError(f"Failed to pop task from {queue_name}: {exc}") from exc

        if result is None:
            return None

        _, task_str = result

        try:
            task = deserialize_task(task_str)
            logger.info(f"Task {task.task_id} popped from {queue_name}")
            return task
        except Exception as exc:
            raise QueueError(f"Invalid task payload from {queue_name}: {exc}") from exc

    # Get queue size
    async def queue_size(self, queue_name: str) -> int:
        try:
            return await self.redis.llen(queue_name)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            raise QueueError(
                f"Failed to get queue size for {queue_name}: {exc}"
            ) from exc

    # Bounded push for embedding queue with backpressure
    async def push_task_bounded_for_embedding_queue(self, task: Task):
        pushed = False

        while not shutdown_manager.is_shutdown_requested():
            size = await self.queue_size(EMBEDDING_QUEUE)

            if size >= EMBEDDING_QUEUE_MAX_SIZE:
                logger.info(f"Embedding queue full ({size}), applying backpressure")
                await asyncio.sleep(0.5)  # backpressure wait
            else:
                await self.push_task(EMBEDDING_QUEUE, task)
                pushed = True
                break

        if not pushed and shutdown_manager.is_shutdown_requested():
            logger.warning("Skipping bounded push because shutdown is in progress")

    # Dead Letter Queue
    async def move_to_dead_letter(self, task: Task):
        try:
            await self.push_task(DEAD_LETTER_QUEUE, task)
            logger.error(f"Task {task.task_id} moved to dead letter queue")
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            raise QueueError(
                f"Failed to move task {task.task_id} to dead letter queue: {exc}"
            ) from exc

    # Utility
    async def clear_queue(self, queue_name: str):
        try:
            await self.redis.delete(queue_name)
            logger.info(f"Cleared queue {queue_name}")
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            raise QueueError(f"Failed to clear queue {queue_name}: {exc}") from exc
