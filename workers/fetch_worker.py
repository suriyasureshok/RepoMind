# workers/fetch_worker.py

import asyncio

from .base_worker import BaseWorker
from models import Task, Stage
from core.utils import WorkspaceManager, WorkerError
from core.constants import PARSE_QUEUE


class FetchWorker(BaseWorker):

    def __init__(self):
        super().__init__(queue_name="fetch_queue")
        self.workspace = WorkspaceManager()

    async def process_task(self, task: Task):
        repo_url = task.payload.get("repo_url")
        if not repo_url:
            raise WorkerError(f"Task {task.task_id} missing repo_url")

        try:
            repo_path = await asyncio.to_thread(self.workspace.clone_repo, repo_url, task.job_id)
        except Exception as exc:
            raise WorkerError(f"Failed to fetch repository for task {task.task_id}: {exc}") from exc

        return {
            "job_id": task.job_id,
            "repo_path": str(repo_path)
        }

    async def enqueue_next(self, result):
        next_task = Task(
            job_id=result["job_id"],
            stage=Stage.PARSE,
            payload=result
        )

        await self.queue.push_task(PARSE_QUEUE, next_task)
