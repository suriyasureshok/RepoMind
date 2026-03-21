import asyncio
from queue_system.queue_manager import QueueManager
from models import Task, Stage

async def test():
    qm = QueueManager()

    task = Task(job_id="123", stage=Stage.FETCH, payload={"repo": "test"})
    await qm.push_task("test_queue", task)

    result = await qm.pop_task("test_queue")
    print(result)

if __name__ == "__main__":
    asyncio.run(test())