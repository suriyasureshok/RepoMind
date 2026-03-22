# core/utils/serializer.py

import json

from models import Task
from core.logging import logger


def serialize_task(task: Task) -> str:
    logger.debug(f"Serializing task {task.task_id}")
    return task.model_dump_json()


def deserialize_task(task_str: str) -> Task:
    data = json.loads(task_str)
    task = Task(**data)
    logger.debug(f"Deserialized task {task.task_id}")
    return task
