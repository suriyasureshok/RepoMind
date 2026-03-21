# models/job.py

from pydantic import BaseModel, Field
from datetime import datetime, timezone
from uuid import uuid4
from typing import Literal


JobStatus = Literal["PENDING", "RUNNING", "FAILED", "COMPLETED", "CANCELLED"]


class Job(BaseModel):
    job_id: str = Field(default_factory=lambda: str(uuid4()))
    status: JobStatus = "PENDING"

    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=datetime.now(timezone.utc))

    def update_status(self, new_status: JobStatus):
        self.status = new_status
        self.updated_at = datetime.now(timezone.utc)
