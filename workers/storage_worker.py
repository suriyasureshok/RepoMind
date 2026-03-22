# workers/storage_worker.py

from .base_worker import BaseWorker
from models import Task
from core.logging import logger
from core.utils import WorkerError


class StorageWorker(BaseWorker):

    def __init__(self):
        super().__init__(queue_name="storage_queue")

    async def process_task(self, task: Task):
        file_path = task.payload.get("file_path")
        if not file_path:
            raise WorkerError(f"Task {task.task_id} missing storage payload")

        logger.info(f"Stored embedding for {file_path}")

        return None

    async def enqueue_next(self, result):
        pass
