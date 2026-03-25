# api/routes/query.py

from fastapi import APIRouter
from api.controllers.schemas import QueryRequest
from pipeline.query_pipeline import run_query_pipeline

router = APIRouter(prefix="/query", tags=["Query"])


@router.post("/")
async def query(request: QueryRequest):
    result = await run_query_pipeline(request.query)

    return {"response": result}
