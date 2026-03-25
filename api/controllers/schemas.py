# api/controllers/schemas.py

from pydantic import BaseModel, HttpUrl


class IngestRequest(BaseModel):
    repo_url: HttpUrl


class JobResponse(BaseModel):
    job_id: str
    status: str


class QueryRequest(BaseModel):
    query: str


class IngestResponse(JobResponse):
    pass


class JobStatusResponse(JobResponse):
    pass
