# api/routes/__init__.py

from fastapi import APIRouter

from .ingest import router as ingest_router
from .job import router as job_router
from .query import router as query_router

router = APIRouter()
router.include_router(ingest_router)
router.include_router(job_router)
router.include_router(query_router)
