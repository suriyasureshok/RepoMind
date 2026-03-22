# models/task.py

from pydantic import BaseModel, Field
from typing import Dict, Any
from uuid import uuid4

from .enums import Stage
from core.logging import logger


class Task(BaseModel):
    task_id: str = Field(default_factory=lambda: str(uuid4()))
    job_id: str
    stage: Stage
    payload: Dict[str, Any]

    retries: int = 0
    max_retries: int = 3

    def increment_retry(self):
        self.retries += 1
        logger.info(f"Task {self.task_id} retry incremented to {self.retries}")

    def can_retry(self) -> bool:
        return self.retries < self.max_retries
