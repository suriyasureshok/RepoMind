# api/routes/ingest.py

from uuid import uuid4

from fastapi import APIRouter

from api.controllers import IngestRequest, IngestResponse
from core.constants import FETCH_QUEUE
from core.utils import JobStore, JobStoreError, QueueError
from models import Stage, Task
from queue_system import QueueManager

router = APIRouter(prefix="/ingest", tags=["Ingestion"])

queue = QueueManager()
job_store = JobStore()


@router.post("/", response_model=IngestResponse)
async def ingest_repo(request: IngestRequest):
    job_id = str(uuid4())
    task = Task(
        job_id=job_id, stage=Stage.FETCH, payload={"repo_url": str(request.repo_url)}
    )

    try:
        await job_store.set_status(job_id, "PENDING")
        await queue.push_task(FETCH_QUEUE, task)
    except QueueError as exc:
        try:
            await job_store.set_status(job_id, "FAILED")
        except JobStoreError as cleanup_exc:
            raise JobStoreError(
                f"Failed to mark job {job_id} as FAILED after queue error: {cleanup_exc}"
            ) from exc
        raise exc
    except JobStoreError:
        raise

    return IngestResponse(job_id=job_id, status="PENDING")
