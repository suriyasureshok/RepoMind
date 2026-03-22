# workers/parse_worker.py

import os

from .base_worker import BaseWorker
from models import Task, Stage
from core.constants import CHUNK_QUEUE
from core.utils import shutdown_manager, WorkerError


class ParseWorker(BaseWorker):

    def __init__(self):
        super().__init__(queue_name="parse_queue")

    async def process_task(self, task: Task):
        repo_path = task.payload.get("repo_path")
        if not repo_path:
            raise WorkerError(f"Task {task.task_id} missing repo_path")

        files = []
        for root, _, filenames in os.walk(repo_path):
            if shutdown_manager.is_shutdown_requested():
                break

            for f in filenames:
                if shutdown_manager.is_shutdown_requested():
                    break

                full_path = os.path.join(root, f)
                files.append(full_path)

        return {
            "job_id": task.job_id,
            "repo_path": repo_path,
            "files": files
        }

    async def enqueue_next(self, result):
        next_task = Task(
            job_id=result["job_id"],
            stage=Stage.CHUNK,
            payload=result
        )

        await self.queue.push_task(CHUNK_QUEUE, next_task)
