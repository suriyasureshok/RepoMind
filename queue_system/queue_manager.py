# queue/queue_manager.py

import asyncio
from typing import Optional

from models import Task
from core.constants import (
    EMBEDDING_QUEUE, 
    EMBEDDING_QUEUE_MAX_SIZE,
    DEAD_LETTER_QUEUE,
)
from core.utils import (
    serialize_task,
    deserialize_task
)
from .redis_client import RedisClient


class QueueManager:

    def __init__(self):
        self.redis = RedisClient.get_client()

    # Push task to queue
    async def push_task(self, queue_name: str, task: Task):
        task_str = serialize_task(task)
        await self.redis.rpush(queue_name, task_str)

    # Pop task (blocking)
    async def pop_task(self, queue_name: str) -> Optional[Task]:
        result = await self.redis.blpop(queue_name, timeout=5)

        if result is None:
            return None

        _, task_str = result
        return deserialize_task(task_str)

    # Get queue size
    async def queue_size(self, queue_name: str) -> int:
        return await self.redis.llen(queue_name)
    
    # Bounded push (for embedding queue)
    async def push_task_bounded(self, queue_name: str, task: Task):
        while True:
            size = await self.queue_size(queue_name)

            if queue_name == EMBEDDING_QUEUE and size >= EMBEDDING_QUEUE_MAX_SIZE:
                await asyncio.sleep(0.5)  # backpressure wait
            else:
                await self.push_task(queue_name, task)
                break

    # Dead Letter Queue
    async def move_to_dead_letter(self, task: Task):
        await self.push_task(DEAD_LETTER_QUEUE, task)

    # Utility
    async def clear_queue(self, queue_name: str):
        await self.redis.delete(queue_name)
