# RepoMind — CONTEXT.md

---

# 1. Project Overview

RepoMind is a **distributed, asynchronous Retrieval-Augmented Generation (RAG) system** designed to understand and query GitHub repositories.

The system ingests a repository, processes its codebase into structured knowledge, and enables intelligent querying using hybrid retrieval and LLM inference.

---

# 2. Core Objective

Build a **production-grade pipeline system** that demonstrates:

* Distributed systems concepts
* Async processing with queues
* Scalable architecture
* Real-world data handling
* AI system integration (RAG)

---

# 3. High-Level System Design

RepoMind consists of two major pipelines:

---

## 3.1 Ingestion Pipeline (Offline, Async)

```text
Fetch → Parse → Chunk → Embed → Store
```

Purpose:

* Convert raw codebase into structured knowledge

---

## 3.2 Query Pipeline (Online, Low Latency)

```text
Query → Retrieval → Rerank → Context → LLM → Response
```

Purpose:

* Answer user queries using processed knowledge

---

# 4. Architecture Principles

---

## 4.1 Pipeline-First Design

The system is built as:

> A task-driven pipeline instead of a monolithic application

---

## 4.2 Queue-Based Decoupling

* Redis is used as the central queue system
* Each stage communicates via queues
* Workers operate independently

---

## 4.3 Asynchronous Execution

* IO-bound tasks → asyncio
* CPU-bound tasks → planned multiprocessing (future)

---

## 4.4 Streaming Processing

* Chunk → Embed → Store happens continuously
* Reduces total latency of ingestion

---

## 4.5 Backpressure Handling

* Bounded embedding queue prevents overload
* Producers slow down automatically

---

## 4.6 Cancellation Propagation

* Job-level cancellation stored in Redis
* Workers check cancellation before and after execution

---

## 4.7 Retry Strategy

* Exponential backoff for failures
* Max retry limit
* Dead Letter Queue for failed tasks

---

# 5. Current Implementation Status

---

## Completed Phases

---

### Phase 0 — Repository Setup

* Monorepo architecture created
* Modular structure defined
* Environment setup completed
* Logging system initialized
* Configuration system implemented

---

### Phase 1 — Core System Primitives

* Task model (Pydantic)
* Job model (status tracking)
* Stage enum (pipeline stages)
* Serialization utilities
* Global constants

---

### Phase 2 — Redis Queue System

* Async Redis client (singleton)
* Queue abstraction:

  * push_task
  * pop_task (blocking)
  * queue_size
* Bounded queue (backpressure)
* Dead Letter Queue support

---

### Phase 3 — Worker Engine

* BaseWorker class
* Worker loop:

  * fetch → validate → execute → enqueue
* Retry mechanism with exponential backoff
* Cancellation handling
* Worker skeletons created

---

### Phase 4 — Workspace Management

* Workspace per job:

  ```
  /workspace/repo_<job_id>/
  ```
* Repo cloning using git
* File utilities:

  * list files
  * read file
* Cleanup system:

  * retry deletion (Windows-safe)
  * read-only file handling
* Startup cleanup for stale workspaces

---

### Phase 5 — Ingestion Pipeline

Implemented full pipeline:

---

#### Fetch Worker

* Clones repo
* Creates workspace
* Pushes parse task

---

#### Parse Worker

* Traverses files
* Collects file paths
* Pushes chunk task

---

#### Chunk Worker (Streaming)

* Reads file content
* Creates chunks (basic implementation)
* Streams chunks to embedding queue

---

#### Embedding Worker

* Uses async semaphore (rate limiting)
* Generates dummy embeddings (placeholder)
* Pushes storage tasks

---

#### Storage Worker

* Simulated storage (logging)
* Placeholder for vector DB and metadata DB

---

# 6. Current Data Flow

```mermaid
flowchart LR
    A[Fetch Worker] --> B[Parse Worker]
    B --> C[Chunk Worker]
    C --> D[Embedding Worker]
    D --> E[Storage Worker]
```

---

# 7. System Components

---

## 7.1 Core

* Configuration system (`BaseSettings`)
* Logging system (centralized logger)
* Constants (queues, workers, limits)

---

## 7.2 Models

* Task (unit of execution)
* Job (global lifecycle control)
* Stage enum

---

## 7.3 Queue System

* Redis-based async queue
* Blocking consumption
* Backpressure support
* DLQ handling

---

## 7.4 Worker System

* Generic BaseWorker
* Stage-specific workers
* Retry + cancellation handling

---

## 7.5 Workspace Layer

* Temporary storage for repos
* File system abstraction
* Safe cleanup handling

---

## 7.6 Pipeline

* Ingestion pipeline implemented
* Query pipeline planned (not implemented yet)

---

# 8. File Structure

```text
repomind/
│
├── api/                     # FastAPI (not implemented yet)
│
├── core/
│   ├── config/
│   ├── logging/
│   ├── utils/
│   └── constants/
│
├── models/
│   ├── task.py
│   ├── job.py
│   └── enums.py
│
├── queue_system/
│   ├── redis_client.py
│   └── queue_manager.py
│
├── workers/
│   ├── base_worker.py
│   ├── fetch_worker.py
│   ├── parse_worker.py
│   ├── chunk_worker.py
│   ├── embedding_worker.py
│   └── storage_worker.py
│
├── services/                # placeholders (not implemented yet)
│   ├── retriever/
│   ├── reranker/
│   ├── llm/
│   └── embedding/
│
├── pipeline/
│   ├── ingestion_pipeline.py (implicit via workers)
│   └── query_pipeline.py (not implemented)
│
├── workspace/               # runtime storage
├── scripts/                 # pipeline runner
├── tests/
├── docs/
└── docker/ (future)
```

---

# 9. Known Limitations (Current)

* Chunking is naive (no function-level parsing)
* Embeddings are dummy
* Storage is not implemented (no DB yet)
* No API layer
* No query pipeline

---

# 10. Next Phases

---

## Phase 6 — API Layer

* Ingestion endpoint
* Job status tracking
* Cancellation endpoint

---

## Phase 7 — Query Pipeline

* Hybrid retrieval (vector + keyword + metadata)
* Reranking
* Context builder
* LLM integration

---

## Phase 8+ — Production Enhancements

* Real vector database
* Metadata indexing
* Caching
* Observability
* Rust optimization

---

# 11. Key Engineering Decisions

---

## Monorepo Architecture

* All services in single repo
* Modular separation for future extraction

---

## Python-First Strategy

* Fast development
* Rust planned for optimization later

---

## Queue-Based Execution

* Decoupled stages
* Fault tolerance
* Scalability

---

## Workspace-Based Processing

* Avoids re-fetching
* Enables retry and debugging

---

# 12. System Identity

RepoMind is:

> A **distributed, asynchronous, queue-driven pipeline system with RAG capabilities**

---

# 13. How to Resume Work

In a new session:

1. Paste this file
2. State current phase
3. Continue implementation

Example:

```
Continuing RepoMind — Phase 6
```

---
