# api/controllers/schemas.py

from pydantic import BaseModel, HttpUrl


class IngestRequest(BaseModel):
    repo_url: HttpUrl


class IngestResponse(BaseModel):
    job_id: str
    status: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
