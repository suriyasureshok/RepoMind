# workers/base_worker.py

import asyncio
from abc import ABC, abstractmethod

from models import Task
from queue_system import QueueManager
from core.logging import logger
from core.utils import shutdown_manager, WorkerError


class BaseWorker(ABC):

    def __init__(self, queue_name: str):
        self.queue_name = queue_name
        self.queue = QueueManager()
        self._running = False

    async def start(self):
        logger.info(f"Starting worker for queue: {self.queue_name}")
        shutdown_manager.install_signal_handlers()
        self._running = True

        while self._running and not shutdown_manager.is_shutdown_requested():
            try:
                task = await self.queue.pop_task(self.queue_name)
            except asyncio.CancelledError:
                logger.info(f"Worker task cancelled for queue: {self.queue_name}")
                break

            if task is None:
                continue

            await self.handle_task(task)

        logger.info(f"Worker loop exited for queue: {self.queue_name}")

    def stop(self):
        logger.info(f"Stopping worker for queue: {self.queue_name}")
        self._running = False

    async def handle_task(self, task: Task):
        try:
            if await self.is_cancelled(task):
                logger.info(f"Task {task.task_id} cancelled before execution")
                return

            result = await self.process_task(task)

            if await self.is_cancelled(task):
                logger.info(f"Task {task.task_id} cancelled after execution")
                return

            if result:
                await self.enqueue_next(result)

        except asyncio.CancelledError:
            raise
        except WorkerError as exc:
            logger.error(f"Worker error for task {task.task_id}: {exc}")
            await self.handle_failure(task)
        except Exception as e:
            logger.error(f"Error processing task {task.task_id}: {e}")
            await self.handle_failure(task)

    async def handle_failure(self, task: Task):
        if shutdown_manager.is_shutdown_requested():
            logger.info(f"Skipping retry for {task.task_id} because shutdown is in progress")
            return

        task.increment_retry()

        if task.can_retry():
            backoff = 2 ** task.retries
            logger.info(f"Retrying task {task.task_id} in {backoff}s")

            await asyncio.sleep(backoff)

            if shutdown_manager.is_shutdown_requested():
                logger.info(f"Retry aborted for {task.task_id} due to shutdown")
                return

            await self.queue.push_task(self.queue_name, task)

        else:
            logger.error(f"Task {task.task_id} moved to DLQ")
            await self.queue.move_to_dead_letter(task)

    async def is_cancelled(self, task: Task) -> bool:
        try:
            status = await self.queue.redis.get(f"job:{task.job_id}:status")
            return status == "CANCELLED"
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            raise WorkerError(f"Failed to read cancellation status for job {task.job_id}: {exc}") from exc

    @abstractmethod
    async def process_task(self, task: Task):
        pass

    @abstractmethod
    async def enqueue_next(self, result):
        pass
