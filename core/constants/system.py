# core/constants/system.py

# Retry Configuration

MAX_RETRIES = 3


# Worker Configuration

FETCH_WORKERS = 2
PARSE_WORKERS = 4
CHUNK_WORKERS = 3
EMBEDDING_WORKERS = 2
STORAGE_WORKERS = 2


# Timeouts (seconds)

FETCH_TIMEOUT = 20
EMBEDDING_TIMEOUT = 15
LLM_TIMEOUT = 30  # Temporary
