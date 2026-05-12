---
id: queue-topology-design
kind: skill
title: Queue Topology Design
description: >
  Split queues by failure mode and cost. Per-queue worker pool with isolated
  concurrency. Recurring jobs subscribed to their own queue. Workers never
  embedded in the web process. Stale-job reapers for DB-backed queues.
applies_when:
  - background job system design
  - adding a new job type with different SLA or cost
  - recurring jobs piling up silently
  - noisy job starving critical path
agents:
  claude: { kind: skill }
  cursor: { kind: rule }
  codex:  { section: skills }
  goose:  { section: skills }
  openclaw: { section: skills }
  opencode: { kind: skill }
  pi:       { section: skills }
  vibe:   { kind: skill }
---

# Queue Topology Design

One queue for everything = one blast radius for everything. Split by what breaks
and how much it costs.

## Split by Failure Mode and Cost

| Queue | Jobs | Worker profile |
|---|---|---|
| `default` | Fast, cheap, non-blocking | Many threads, short timeout |
| `fetch` | External HTTP, variable latency | Fewer threads, longer timeout |
| `realtime` | User-facing, latency-sensitive | Dedicated, high priority |
| `recurring` | Scheduled, low urgency | Low concurrency, can lag |

Add a queue when: SLA differs, failure blast radius must be contained, or a
noisy job would starve another class.

## Per-Queue Worker Pool

Each queue gets its own worker process or thread pool. A long-running `fetch`
job must not block a `realtime` slot.

```python
WORKER_POOLS = {
    "default":   WorkerPool(concurrency=10, timeout=30),
    "fetch":     WorkerPool(concurrency=4,  timeout=120),
    "realtime":  WorkerPool(concurrency=8,  timeout=10),
    "recurring": WorkerPool(concurrency=2,  timeout=300),
}
```

## Recurring Jobs Need Their Own Subscriber

A recurring job enqueued to `recurring` silently piles up if no worker is
subscribed to that queue. Always verify: enqueued queue ↔ worker queue list.

## Workers Outside the Web Process

Embedding a worker thread in the web process couples their memory, crash domain,
and deploy cycle. Run workers as separate processes. Scale them independently.

## Stale-Job Reaper

DB-backed queues (job status stored in a table) accumulate `running` rows when
workers crash. A reaper reclaims them; target only `ready` or long-`running`
rows to avoid stampede.

```python
def reap_stale(repo: JobRepo, queue: Queue, cutoff: datetime) -> int:
    stale = repo.stale(status="running", before=cutoff)
    for job in stale:
        queue.reenqueue(job.id)
    return len(stale)
```

For multi-step saga reaping, see skill:pipeline-saga-orchestration.

## Observability

Each queue is a first-class boundary: span per enqueue/dequeue, RED metrics
per queue (rate, error rate, duration). Alert on queue depth + worker error
rate, not raw counts (see rule:observability).

## GOOD

`fetch` jobs on their own queue + worker pool with 120 s timeout. `realtime`
queue never touches the fetch pool. Reaper runs every minute on the `fetch`
worker table. No background thread in the web dyno.

## BAD

```python
Thread(target=process_jobs, daemon=True).start()  # inside web process
```

Worker shares web process memory and crash domain. No queue separation.
Long fetch job starves real-time response. Stale rows accumulate silently.

## Red Flags

- All job types share a single queue and worker pool.
- Recurring job enqueued to `default`; no worker subscribed to its queue.
- Worker thread started inside the HTTP server process.
- No stale-row reaper; `running` jobs accumulate after worker crashes.
- Queue depth metric missing; pileup invisible until user reports slowness.
