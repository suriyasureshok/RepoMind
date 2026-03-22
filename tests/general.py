import asyncio

from workers import FetchWorker
from workers import ParseWorker
from workers import ChunkWorker
from workers import EmbeddingWorker
from workers import StorageWorker

from models import Task, Stage
from core.utils import shutdown_manager
from queue_system import RedisClient


async def main():
    shutdown_manager.clear()
    shutdown_manager.install_signal_handlers()

    fetch = FetchWorker()
    parse = ParseWorker()
    chunk = ChunkWorker()
    embed = EmbeddingWorker()
    store = StorageWorker()
    workers = [fetch, parse, chunk, embed, store]

    # start workers
    worker_tasks = [asyncio.create_task(worker.start()) for worker in workers]

    # seed task
    task = Task(
        job_id="job1",
        stage=Stage.FETCH,
        payload={"repo_url": "https://github.com/git/git"}
    )

    await fetch.queue.push_task("fetch_queue", task)

    try:
        await asyncio.wait_for(shutdown_manager.wait_for_shutdown(), timeout=30)
    except asyncio.TimeoutError:
        shutdown_manager.request_shutdown("worker-demo-timeout")
    finally:
        for worker in workers:
            worker.stop()

        for worker_task in worker_tasks:
            worker_task.cancel()

        await asyncio.gather(*worker_tasks, return_exceptions=True)
        await RedisClient.close_client()


asyncio.run(main())