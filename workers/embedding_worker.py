# workers/embedding_worker.py

import asyncio

from core.constants import STORAGE_QUEUE
from core.utils import WorkerError
from models import Stage, Task

from .base_worker import BaseWorker


class EmbeddingWorker(BaseWorker):

    def __init__(self):
        super().__init__(queue_name="embedding_queue")
        self.semaphore = asyncio.Semaphore(5)

    async def fake_embedding(self, text: str):
        await asyncio.sleep(0.1)
        return [0.1] * 10  # dummy vector

    async def process_task(self, task: Task):
        async with self.semaphore:
            chunk = task.payload.get("chunk")
            file_path = task.payload.get("file_path")

            if chunk is None or file_path is None:
                raise WorkerError(f"Task {task.task_id} missing embedding payload")

            embedding = await self.fake_embedding(chunk)

            return {
                "job_id": task.job_id,
                "file_path": file_path,
                "embedding": embedding,
                "chunk": chunk,
            }

    async def enqueue_next(self, result):
        next_task = Task(job_id=result["job_id"], stage=Stage.STORE, payload=result)

        await self.queue.push_task(STORAGE_QUEUE, next_task)
