---
id: concurrency-correctness
kind: skill
title: Concurrency Correctness
description: >
  Shared mutable state, structured concurrency, lock ordering, atomicity vs
  ordering, async-specific traps, optimistic concurrency for shared records.
applies_when:
  - async or threaded code
  - shared mutable state
  - concurrent writes to the same record
  - cancellation or timeout handling
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

# Concurrency Correctness

Shared state is a contract. Make it explicit or eliminate it.

## Shared Mutable State

Default: **immutable data, message-passing**. Shared mutable state only when the
performance or API constraint is unavoidable. Name every lock. Document the invariant
it protects. Prefer actor or queue-based ownership over raw shared references.

## Structured Concurrency

Prefer `TaskGroup` over bare `asyncio.create_task`. Child tasks live inside the scope;
exceptions propagate; scope exits when all children finish. Dangling tasks leak
resources and swallow errors.

```python
async with asyncio.TaskGroup() as tg:
    tg.create_task(fetch_user(uid))
    tg.create_task(fetch_prefs(uid))
```

## Cancellation Propagation

`asyncio.CancelledError` must propagate. Catch only to clean up, then re-raise.
`finally` handles teardown. Swallowing `CancelledError` = silent hang.

```python
try:
    await long_op()
except asyncio.CancelledError:
    await cleanup()
    raise
```

## Lock Ordering

Multiple locks → always acquire in the same global order. Inconsistent order = deadlock.

```text
GOOD: every caller acquires lock_A before lock_B
BAD: thread 1 → A then B; thread 2 → B then A → deadlock
```

## Atomicity vs Ordering

**Atomicity**: all-or-nothing write. Use DB transactions or OS atomic ops.
**Ordering**: happens-before guarantee. Acquire + release of the same lock provides both.

A Python `threading.Lock` guards in-process state; the DB has its own races.
Don't confuse the two. See skill:unit-of-work-and-transactions for DB-level atomicity.

## Async-Specific Traps

| Trap | Fix |
|---|---|
| Forgotten `await` | type checker catches it; never ignore the warning |
| Blocking call in async path | `loop.run_in_executor` for CPU or blocking I/O |
| Busy-poll via `asyncio.sleep(0)` | yield once then listen; restructure the loop |
| `global` dict mutated in handler | lock or actor; no bare mutation |

## Optimistic Concurrency

For DB records: version column incremented on every write. Update `WHERE id = ? AND version = ?`.
Zero rows updated → conflict; retry or reject. Avoids pessimistic locks on hot records.

```python
rows = conn.execute(
    "UPDATE items SET data=?, version=version+1 WHERE id=? AND version=?",
    (new_data, item_id, expected_version),
).rowcount
if rows == 0:
    raise ConflictError("stale version")
```

See skill:resilience-retries for the retry policy around conflicts.
See skill:pipeline-saga-orchestration for multi-step distributed atomicity.

## GOOD

```python
async def process_batch(ids: list[str]) -> list[Result]:
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(process_one(i)) for i in ids]
    return [t.result() for t in tasks]
```

Structured scope. All tasks finish or all are cancelled together.

## BAD

```python
tasks = [asyncio.create_task(process_one(i)) for i in ids]
results = await asyncio.gather(*tasks, return_exceptions=True)
```

Bare tasks escape scope. Cancellation of the caller leaves children running.

## Red Flags

- `asyncio.create_task` with no parent scope tracking the child.
- `except Exception: pass` around `await` — swallows `CancelledError`.
- Two threads acquire different lock sets in different order.
- `time.sleep` inside an async function.
- DB read-modify-write without version column or `SELECT FOR UPDATE`.
- `global` dict mutated from multiple coroutines without a lock.
