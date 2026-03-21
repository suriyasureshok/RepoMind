# core/constants/__init__.py

from .queues import (
    FETCH_QUEUE,
    PARSE_QUEUE,
    CHUNK_QUEUE,
    EMBEDDING_QUEUE,
    STORAGE_QUEUE,
    DEAD_LETTER_QUEUE,
    EMBEDDING_QUEUE_MAX_SIZE,
)

from .system import (
    MAX_RETRIES,
    FETCH_WORKERS,
    PARSE_WORKERS,
    CHUNK_WORKERS,
    EMBEDDING_WORKERS,
    STORAGE_WORKERS,
)

__all__ = [
    # Queue Constants

    "FETCH_QUEUE",
    "PARSE_QUEUE",
    "CHUNK_QUEUE",
    "EMBEDDING_QUEUE",
    "STORAGE_QUEUE",
    "DEAD_LETTER_QUEUE",

    # Backpressure Threshold
    "EMBEDDING_QUEUE_MAX_SIZE",

    # System Constants

    "MAX_RETRIES",
    "FETCH_WORKERS",
    "PARSE_WORKERS",
    "CHUNK_WORKERS",
    "EMBEDDING_WORKERS",
    "STORAGE_WORKERS",
]
