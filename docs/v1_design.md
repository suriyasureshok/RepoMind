# RepoMind — End-to-End System Design (V1)

---

# 1. System Overview

RepoMind is a **distributed, asynchronous RAG-based system** designed to understand and query GitHub repositories.

It consists of two major pipelines:

1. **Ingestion Pipeline (Offline, Async, Heavy)**
2. **Query Pipeline (Online, Low Latency)**

The system is built using:

* Queue-driven architecture (Redis)
* Hybrid concurrency (asyncio + multiprocessing)
* Task-based execution model
* Streaming and backpressure control

---

# 2. Core Design Philosophy

The system is designed as:

> A **pipeline-first distributed system**, not a monolithic RAG application.

Key principles:

* Decoupled stages via queues
* Backpressure-aware execution
* Cancellation-aware processing
* Hybrid retrieval for accuracy
* Streaming for latency optimization

---

# 3. Data Flow Model

```text
Users → Jobs → Tasks → Queues → Workers → Storage → Retrieval → LLM
```

* Each user request creates a **job**
* Each job is broken into **tasks**
* Tasks move through **queues**
* Workers process tasks independently

---

# 4. Ingestion Pipeline (Detailed)

---

## 4.1 Workflow

```text
API → Job Creation → Fetch → Workspace → Parse → Chunk → Embed → Store → Cleanup
```

---

## 4.2 Workspace Layer

After fetching, repositories are stored in:

```text
/workspace/repo_{job_id}/
```

Purpose:

* Acts as temporary storage
* Enables retry and deterministic processing
* Avoids re-fetching

Lifecycle:

* Created at fetch
* Used during parse/chunk
* Deleted after completion/failure/cancellation

---

## 4.3 Pipeline Stages

---

### Stage 1 — Fetch

* Downloads repository from GitHub
* Stores in workspace

Execution:

* Async workers (2)
* IO-bound
* Retry with exponential backoff

---

### Stage 2 — Parse

* Reads files from workspace
* Extracts structure (modules, classes, functions)

Execution:

* Multiprocessing workers (3–4)
* CPU-bound

---

### Stage 3 — Chunk + Metadata

* Splits code into function-level chunks
* Splits README by sections
* Attaches metadata

Metadata includes:

* file path
* language
* module/class/function
* chunk type
* line numbers

Execution:

* Multiprocessing workers (3)

Output:

* Streams chunks to embedding stage

---

### Stage 4 — Embedding

* Converts chunks into vector embeddings

Execution:

* Async workers (2)
* Rate-limited using semaphore
* Uses streaming input

Backpressure:

* Bounded embedding queue prevents overload

---

### Stage 5 — Storage

* Stores:

  * vectors → vector DB
  * metadata → metadata DB
  * keywords → inverted index

Execution:

* Async workers (2)
* Decoupled from embedding via queue

---

## 4.4 Key Design Features

---

### Streaming Pipeline

* Chunk → Embed → Store happens continuously
* Reduces total ingestion latency

---

### Backpressure Control

* Embedding queue is bounded
* Upstream workers slow down automatically

---

### Cancellation Propagation

* Global job status stored in Redis
* Workers check before and after execution
* Prevents unnecessary downstream work

---

### Retry Strategy

* IO stages: exponential backoff
* CPU stages: limited retry

---

---

# 5. Query Pipeline (Detailed)

---

## 5.1 Workflow

```text
Query → Preprocess → Hybrid Retrieval → Rerank → Context Build → LLM → Response
```

---

## 5.2 Query Preprocessing

* Cleans query
* Detects intent (code / explanation)
* Applies optional filters (language, path)

---

## 5.3 Hybrid Retrieval (Parallel)

Three retrieval strategies run in parallel:

---

### 1. Vector Search

* Semantic similarity
* Top-K: ~50

---

### 2. Keyword Search

* Exact match (BM25/inverted index)
* Top-K: ~50

---

### 3. Metadata Filtering

* Filters by language, file, module
* Adds relevance signals

---

## 5.4 Merge and Rerank

Steps:

1. Combine results
2. Remove duplicates
3. Apply scoring:

```text
Final Score = 0.7 * Vector + 0.3 * Keyword + Metadata Boost
```

4. Select Top 10–20 chunks

---

## 5.5 Context Builder

* Orders chunks
* Trims to token limit
* Adds file references

---

## 5.6 LLM Load Balancer

* Chooses between 2 LLM servers
* Strategy: Least Active Requests
* Failover supported

---

## 5.7 LLM Inference

* Generates answer
* Streams tokens to user

---

## 5.8 Caching Strategy

* Query cache: (query + repo_id)
* Retrieval cache: query → chunks

---

---

# 6. Execution Model

---

## Hybrid Concurrency

| Type            | Usage           |
| --------------- | --------------- |
| asyncio         | IO-bound tasks  |
| multiprocessing | CPU-bound tasks |

---

## Worker Model

* Workers consume from Redis queues
* Each stage has dedicated worker pool

---

## Queue Structure

```text
fetch_queue
parse_queue
chunk_queue
embedding_queue (bounded)
storage_queue
dead_letter_queue
```

---

---

# 7. System Controls

---

## Cancellation

* Global job status in Redis
* Workers terminate processing if cancelled

---

## Backpressure

* Controlled via bounded queues
* Prevents overload

---

## Rate Limiting

* Applied to embedding and LLM calls

---

## Retry Handling

* Exponential backoff for IO failures
* Limited retries for CPU tasks

---

---

# 8. Multi-User Behavior

* System is job-based, not user-isolated
* Multiple users share:

  * queues
  * workers
* Isolation via job_id

Future improvements:

* per-user rate limits
* fair scheduling

---

---

# 9. Trade-offs

| Decision            | Trade-off                    |
| ------------------- | ---------------------------- |
| Redis queues        | simple but not fully durable |
| Lazy cancellation   | small compute waste          |
| Hybrid concurrency  | added complexity             |
| Parallel retrieval  | more compute usage           |
| Streaming ingestion | harder debugging             |

---

---

# 10. Rejected Approaches

* Monolithic pipeline → no fault isolation
* Sequential retrieval → poor accuracy
* In-memory queues → no resilience
* Single embedding worker → bottleneck
* No metadata → weak retrieval

---

---

# 11. Future Enhancements

* Kafka for queueing
* Distributed deployment
* Auto-scaling workers
* Advanced reranking models
* Cross-repo knowledge linking

---

---

# 12. Final System Identity

RepoMind is:

> A **distributed, asynchronous, queue-driven system with hybrid retrieval and streaming LLM inference**

It is designed to:

* Handle multiple jobs concurrently
* Optimize latency via streaming
* Maintain stability via backpressure
* Provide high-quality answers via hybrid retrieval

---
