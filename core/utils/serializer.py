# core/utils/serializer.py

import json

from core.logging import logger
from models import Task


def serialize_task(task: Task) -> str:
    logger.debug(f"Serializing task {task.task_id}")
    return task.model_dump_json()


def deserialize_task(task_str: str) -> Task:
    data = json.loads(task_str)
    task = Task(**data)
    logger.debug(f"Deserialized task {task.task_id}")
    return task
