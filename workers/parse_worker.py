# workers/parse_worker.py

import asyncio
import os

from .base_worker import BaseWorker
from models import Task, Stage
from core.constants import CHUNK_QUEUE
from core.utils import shutdown_manager, WorkerError


class ParseWorker(BaseWorker):

    def __init__(self):
        super().__init__(queue_name="parse_queue")

    def _collect_files(self, repo_path: str) -> tuple[list[str], bool]:
        files: list[str] = []

        for root, _, filenames in os.walk(repo_path):
            if shutdown_manager.is_shutdown_requested():
                return files, True

            for f in filenames:
                if shutdown_manager.is_shutdown_requested():
                    return files, True

                full_path = os.path.join(root, f)
                files.append(full_path)

        return files, False

    async def process_task(self, task: Task):
        repo_path = task.payload.get("repo_path")
        if not repo_path:
            raise WorkerError(f"Task {task.task_id} missing repo_path")

        repo_path = os.path.abspath(repo_path)
        if not os.path.exists(repo_path) or not os.path.isdir(repo_path):
            raise WorkerError(f"Task {task.task_id} has invalid repo_path: {repo_path}")

        files, incomplete = await asyncio.to_thread(self._collect_files, repo_path)

        if incomplete:
            return {
                "job_id": task.job_id,
                "repo_path": repo_path,
                "files": files,
                "incomplete": True,
            }

        return {
            "job_id": task.job_id,
            "repo_path": repo_path,
            "files": files
        }

    async def enqueue_next(self, result):
        if result.get("incomplete"):
            return

        next_task = Task(
            job_id=result["job_id"],
            stage=Stage.CHUNK,
            payload=result
        )

        await self.queue.push_task(CHUNK_QUEUE, next_task)
