# core/utils/serializer.py

import json

from models import Task


def serialize_task(task: Task) -> str:
    return task.model_dump_json()


def deserialize_task(task_str: str) -> Task:
    data = json.loads(task_str)
    return Task(**data)
