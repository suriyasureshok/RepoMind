# RepoMind — Implementation Phases (Final Structured Plan)

---

# 🧱 PHASE 0 — FOUNDATION (Repo + Environment)

## Goal:

Establish a clean, scalable monorepo foundation.

### Tasks:

* Initialize monorepo structure
* Setup Python environment (venv/poetry)
* Install dependencies:

  * fastapi, uvicorn
  * redis (async)
  * pydantic
  * httpx, aiofiles
* Create `.env` and config loader
* Setup structured logging
* Create base folders:

  * api/
  * core/
  * models/
  * queue/
  * workers/
  * services/
  * pipeline/
  * workspace/
  * docs/

---

# 🧱 PHASE 1 — CORE SYSTEM PRIMITIVES

## Goal:

Define the fundamental building blocks of the system.

### Tasks:

* Define Task model (task_id, job_id, stage, payload, retries)
* Define Job model (job_id, status)
* Define Stage Enum (FETCH, PARSE, CHUNK, EMBED, STORE)
* Create serialization/deserialization utilities
* Define global constants (queue names, limits)

---

# 🧱 PHASE 2 — REDIS QUEUE SYSTEM

## Goal:

Build a reliable async queue layer.

### Tasks:

* Create Redis async connection manager
* Implement queue abstraction:

  * push_task()
  * pop_task()
  * queue_size()
* Implement task serialization (JSON)
* Define queue names:

  * fetch_queue
  * parse_queue
  * chunk_queue
  * embedding_queue (bounded)
  * storage_queue
  * dead_letter_queue
* Implement bounded queue logic (backpressure)

---

# 🧱 PHASE 3 — WORKER ENGINE (CORE EXECUTION)

## Goal:

Create a generic, reusable worker system.

### Tasks:

* Build BaseWorker class:

  * start loop
  * stop control
  * process_task()
* Implement worker loop:

  * fetch → validate → execute → push next
* Add retry mechanism:

  * exponential backoff
  * retry counter
  * DLQ handling
* Implement cancellation:

  * Redis job status check (before + after)
* Create worker types:

  * FetchWorker
  * ParseWorker
  * ChunkWorker
  * EmbeddingWorker
  * StorageWorker

---

# 🧱 PHASE 4 — WORKSPACE MANAGEMENT

## Goal:

Handle repo storage and lifecycle.

### Tasks:

* Create workspace manager:

  * create repo directory
  * delete repo directory
* Implement repo cloning into workspace
* Add file utilities:

  * read file
  * list directory
* Implement cleanup triggers:

  * on completion
  * on failure
  * on cancellation
* Add startup cleanup for stale folders

---

# 🧱 PHASE 5 — INGESTION PIPELINE

## Goal:

Build full ingestion flow with streaming + backpressure.

### Tasks:

* Implement Fetch Worker:

  * clone repo
  * push parse task

* Implement Parse Worker:

  * read files
  * extract structure
  * push chunk task

* Implement Chunk Worker:

  * function-level chunking
  * README splitting
  * metadata generation
  * stream chunks to embedding queue

* Implement Embedding Worker:

  * load embedding model
  * apply semaphore (rate limiting)
  * generate embeddings
  * push to storage queue

* Implement Storage Worker:

  * store vectors
  * store metadata
  * update keyword index

---

# 🧱 PHASE 6 — API LAYER

## Goal:

Expose system functionality.

### Tasks:

* Setup FastAPI app
* Implement endpoints:

  * POST /ingest → create job + enqueue fetch
  * GET /status/{job_id}
  * POST /cancel/{job_id}
* Add request validation
* Add response schema

---

# 🧱 PHASE 7 — QUERY PIPELINE

## Goal:

Enable intelligent querying over indexed repos.

### Tasks:

* Implement query endpoint (POST /query)

* Build Query Preprocessor:

  * clean query
  * detect intent
  * apply filters

* Implement Retrieval Services:

  * vector search
  * keyword search
  * metadata filtering

* Execute retrieval in parallel (asyncio.gather)

* Build Reranker:

  * merge results
  * score fusion
  * select top-K

* Build Context Builder:

  * token trimming
  * formatting

* Implement LLM Service:

  * API client
  * streaming response

* Implement Load Balancer:

  * least active requests
  * failover

---

# 🧱 PHASE 8 — SYSTEM CONTROLS

## Goal:

Make system stable under load.

### Tasks:

* Implement rate limiting:

  * embedding semaphore
  * LLM concurrency limit
* Implement backpressure:

  * bounded embedding queue
* Implement retry + DLQ handling
* Add timeout controls

---

# 🧱 PHASE 9 — CACHING

## Goal:

Reduce redundant computation.

### Tasks:

* Query cache (query + repo_id)
* Retrieval cache (query → chunks)
* Optional embedding cache

---

# 🧱 PHASE 10 — OBSERVABILITY

## Goal:

Make system debuggable and measurable.

### Tasks:

* Add structured logging (task lifecycle)
* Track metrics:

  * queue sizes
  * processing latency
  * worker utilization

---

# 🧱 PHASE 11 — TESTING

## Goal:

Ensure correctness and resilience.

### Tasks:

* Unit tests:

  * queue
  * worker logic
* Integration tests:

  * ingestion pipeline
  * query pipeline
* Failure tests:

  * cancellation
  * retries
  * API failure simulation

---

# 🧱 PHASE 12 — OPTIMIZATION (POST V1)

## Goal:

Improve performance based on real bottlenecks.

### Tasks:

* Profile system:

  * CPU usage
  * latency hotspots

* Migrate to Rust (if needed):

  * parser
  * chunker
  * keyword index

* Improve scaling:

  * increase workers
  * distributed deployment

---

# 🚀 FINAL BUILD ORDER

0 → Foundation
1 → Models
2 → Queue
3 → Workers
4 → Workspace
5 → Ingestion
6 → API
7 → Query
8 → Controls
9 → Caching
10 → Observability
11 → Testing
12 → Optimization

---

# 🧠 SYSTEM COMPLETION STATE

After Phase 7:
→ Functional system

After Phase 10:
→ Production-grade

After Phase 12:
→ Performance-optimized

---
