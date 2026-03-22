# api/routes/job.py

from fastapi import APIRouter

from core.utils import JobStore
from api.controllers import JobStatusResponse

router = APIRouter(prefix="/job", tags=["Job"])

job_store = JobStore()


@router.get("/{job_id}", response_model=JobStatusResponse)
async def get_status(job_id: str):
    status = await job_store.get_status(job_id)

    if status is None:
        raise JobNotFoundError(job_id)

    return JobStatusResponse(job_id=job_id, status=status)


@router.post("/{job_id}/cancel")
async def cancel_job(job_id: str):
    await job_store.cancel_if_cancellable(job_id)

    return {"message": "Job cancelled"}
