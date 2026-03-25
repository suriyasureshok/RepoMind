# workers/base_worker.py

import asyncio
from abc import ABC, abstractmethod

from core.logging import logger
from core.utils import WorkerError, shutdown_manager
from models import Task
from queue_system import QueueManager

MAX_BACKOFF_SECONDS = 30


class BaseWorker(ABC):

    def __init__(self, queue_name: str):
        self.queue_name = queue_name
        self.queue = QueueManager()
        self._running = False
        self._pending_requeues: set[asyncio.Task] = set()

    async def start(self):
        logger.info(f"Starting worker for queue: {self.queue_name}")
        shutdown_manager.install_signal_handlers()
        self._running = True
        pop_error_backoff = 1.0

        try:
            while self._running and not shutdown_manager.is_shutdown_requested():
                try:
                    task = await self.queue.pop_task(self.queue_name)
                    pop_error_backoff = 1.0
                except asyncio.CancelledError:
                    logger.info(f"Worker task cancelled for queue: {self.queue_name}")
                    break
                except Exception as exc:
                    logger.exception(
                        f"Failed to pop task from queue {self.queue_name}: {exc}"
                    )
                    await asyncio.sleep(pop_error_backoff)
                    pop_error_backoff = min(pop_error_backoff * 2, 5.0)
                    continue

                if task is None:
                    continue

                await self.handle_task(task)
        finally:
            await self._cleanup_pending_requeues()
            logger.info(f"Worker loop exited for queue: {self.queue_name}")

    def stop(self):
        logger.info(f"Stopping worker for queue: {self.queue_name}")
        self._running = False

    async def _cleanup_pending_requeues(self):
        if not self._pending_requeues:
            return

        pending_tasks = list(self._pending_requeues)

        for pending_task in pending_tasks:
            pending_task.cancel()

        await asyncio.gather(*pending_tasks, return_exceptions=True)
        self._pending_requeues.difference_update(pending_tasks)

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

    async def _delayed_requeue(self, task: Task, delay_seconds: int):
        try:
            await asyncio.sleep(delay_seconds)

            if shutdown_manager.is_shutdown_requested():
                logger.info(f"Retry aborted for {task.task_id} due to shutdown")
                return

            await self.queue.push_task(self.queue_name, task)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.error(f"Failed delayed requeue for {task.task_id}: {exc}")

    async def handle_failure(self, task: Task):
        if shutdown_manager.is_shutdown_requested():
            logger.info(
                f"Skipping retry for {task.task_id} because shutdown is in progress"
            )
            return

        task.increment_retry()

        if task.can_retry():
            backoff = min(2**task.retries, MAX_BACKOFF_SECONDS)
            logger.info(f"Retrying task {task.task_id} in {backoff}s")
            requeue_task = asyncio.create_task(self._delayed_requeue(task, backoff))
            self._pending_requeues.add(requeue_task)
            requeue_task.add_done_callback(
                lambda completed_task: self._pending_requeues.discard(completed_task)
            )

        else:
            logger.error(f"Task {task.task_id} moved to DLQ")
            await self.queue.move_to_dead_letter(task)

    async def is_cancelled(self, task: Task) -> bool:
        try:
            status = await self.queue.redis.get(f"job:{task.job_id}:status")

            if isinstance(status, bytes):
                status = status.decode("utf-8", errors="replace")

            return status == "CANCELLED"
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            raise WorkerError(
                f"Failed to read cancellation status for job {task.job_id}: {exc}"
            ) from exc

    @abstractmethod
    async def process_task(self, task: Task):
        pass

    @abstractmethod
    async def enqueue_next(self, result):
        pass
