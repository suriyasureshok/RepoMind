# chunk_worker.py

import asyncio

from workers.base_worker import BaseWorker
from models import Task, Stage
from core.utils import shutdown_manager, WorkerError
from core.logging import logger


class ChunkWorker(BaseWorker):

    def __init__(self):
        super().__init__(queue_name="chunk_queue")

    async def process_task(self, task: Task):
        files = task.payload.get("files")
        if files is None:
            raise WorkerError(f"Task {task.task_id} missing files payload")

        for file_path in files:
            if shutdown_manager.is_shutdown_requested():
                break

            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                chunk = content[:1000]  # simple chunk (for now)

                chunk_payload = {
                    "job_id": task.job_id,
                    "file_path": file_path,
                    "chunk": chunk
                }

                chunk_task = Task(
                    job_id=task.job_id,
                    stage=Stage.EMBED,
                    payload=chunk_payload
                )

                await self.queue.push_task_bounded_for_embedding_queue(chunk_task)

            except asyncio.CancelledError:
                raise
            except OSError as exc:
                logger.warning(f"Failed to read file for task {task.task_id} at {file_path}: {exc}")
                continue

        return None

    async def enqueue_next(self, result):
        pass  # streaming stage, nothing to enqueue
