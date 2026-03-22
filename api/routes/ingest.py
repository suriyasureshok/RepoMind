# api/routes/ingest.py

from fastapi import APIRouter
from uuid import uuid4

from models import Task, Stage
from queue_system import QueueManager
from core.utils import JobStore, JobStoreError, QueueError
from api.controllers import IngestRequest, IngestResponse
from core.constants import FETCH_QUEUE

router = APIRouter(prefix="/ingest", tags=["Ingestion"])

queue = QueueManager()
job_store = JobStore()


@router.post("/", response_model=IngestResponse)
async def ingest_repo(request: IngestRequest):
    job_id = str(uuid4())

    try:
        await job_store.set_status(job_id, "PENDING")

        task = Task(
            job_id=job_id,
            stage=Stage.FETCH,
            payload={"repo_url": str(request.repo_url)}
        )

        await queue.push_task(FETCH_QUEUE, task)
    except (JobStoreError, QueueError):
        raise

    return IngestResponse(job_id=job_id, status="PENDING")
