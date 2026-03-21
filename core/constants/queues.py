# core/cpnstants/queues.py

# Queue Names

FETCH_QUEUE = "fetch_queue"
PARSE_QUEUE = "parse_queue"
CHUNK_QUEUE = "chunk_queue"
EMBEDDING_QUEUE = "embedding_queue"
STORAGE_QUEUE = "storage_queue"
DEAD_LETTER_QUEUE = "dead_letter_queue"


# Backpressure Threshold

EMBEDDING_QUEUE_MAX_SIZE = 500
