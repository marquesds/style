---
id: pipeline-saga-orchestration
kind: skill
title: Pipeline Saga Orchestration
description: >
  Multi-step jobs that survive deploys. One step = one persisted record with
  lifecycle. Claim under lock, idempotent re-run, stale-step reaper, max-step
  budget. Distinct from a single-use-case UoW or a single-call retry.
applies_when:
  - long-running jobs that span requests or deploys
  - multi-step processing pipeline
  - workflows that must resume after crash or restart
  - background job with partial-progress checkpointing
agents:
  claude: { kind: skill }
  cursor: { kind: skill }
  codex:  { section: skills }
  goose:  { section: skills }
  openclaw: { section: skills }
  opencode: { kind: skill }
  pi:       { section: skills }
  vibe:   { kind: skill }
---

# Pipeline Saga Orchestration

Long-running jobs need checkpoints. A saga = sequence of steps, each persisted
and claimable independently.

## Step Lifecycle

Each step row carries: `id`, `pipeline_id`, `status`, `attempts`, `started_at`, `completed_at`.

| Status | Meaning |
|---|---|
| `pending` | Not yet claimed |
| `running` | Claimed; may be stale if no heartbeat |
| `completed` | Done; re-run returns early |
| `failed` | Max attempts exhausted |

## Claim Under Lock

Claim atomically before executing. Treat `running` steps not updated within
the stale window as reclaimable.

```python
def claim(step: Step, stale_after: timedelta, at: datetime) -> bool:
    if step.completed:
        return False
    if step.running and not _is_stale(step, stale_after, at):
        return False
    return repo.claim_atomically(step.id, at)
```

## Idempotent Re-run

```python
def run_step(step: Step, handler: StepHandler, ctx: RunCtx) -> StepResult:
    if not claim(step, ctx.stale_after, ctx.now):
        return StepResult.skipped(step.id)
    result = handler.execute(step)
    repo.record(step.id, result.status, at=ctx.now)
    return result
```

`handler.execute` must be idempotent — same input, same outcome, no duplicate side effects.

## Resume Sweeper

Recurring job scans for pipelines with stale `running` steps and re-enqueues them.
One sweeper per pipeline type; cadence shorter than the stale window.

```python
def sweep_interrupted(repo: StepRepo, queue: Queue, at: datetime) -> int:
    stale = repo.stale_running(cutoff=at - STALE_WINDOW)
    for step in stale:
        queue.enqueue(step.id)
    return len(stale)
```

## Max-Step Budget

Hard limit on `attempts` per step. Exceed → mark `failed` and alert.
Prevents infinite loops that neither UoW nor single-call retries protect against
across deploys (skill:unit-of-work-and-transactions, skill:resilience-retries).

## Scope Boundaries

| Concern | Skill |
|---|---|
| Single request atomicity | skill:unit-of-work-and-transactions |
| Single outbound call retry | skill:resilience-retries |
| Worker pool isolation | skill:queue-topology-design |
| Multi-step durable job | **this skill** |

## GOOD

One row per step. Claim atomically. Sweeper re-enqueues stale. Max-attempt guard
halts runaway. Side effects fire inside handler only after claim succeeds.

## BAD

```python
def run_pipeline(steps):
    for step in steps:
        step.execute()
```

No persistence. Crash loses all progress. No claim, no idempotency, no stale
detection. Restart reruns every step from scratch.

## Red Flags

- Pipeline state held only in memory or a single request's transaction.
- `running` rows accumulate; no sweeper rescues stale steps.
- Re-running a step duplicates side effects (handler not idempotent).
- No max-attempt cap; a failing step retries indefinitely.
- Sweeper targets a queue different from the workers consuming it.
