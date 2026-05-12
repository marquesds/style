---
id: unit-of-work-and-transactions
kind: skill
title: Unit of Work + Transactions
description: >
  One UoW per use case. Atomic boundary. Repositories registered in the UoW.
  Commit at the end of the use case, never inside the domain.
applies_when:
  - use case touches multiple aggregates
  - need atomicity across writes
  - need outbox or event publish with persistence
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

# Unit of Work + Transactions

One use case → one UoW → one transaction. Domain stays pure.

## The Port

```python
class UnitOfWork(Protocol):
    sessions: SessionRepo
    audit: AuditRepo
    outbox: OutboxRepo

    def __enter__(self) -> "UnitOfWork": ...
    def __exit__(self, exc_type, exc, tb) -> None: ...
    def commit(self) -> None: ...
    def rollback(self) -> None: ...
```

`__exit__` calls `rollback` if an exception escaped, otherwise leaves it to the caller. Explicit `commit()` at the end of the use case.

## Use Case Shape

```python
def reset_session(uow_factory: Callable[[], UnitOfWork],
                  clock: Clock,
                  id: SessionId) -> Session:
    with uow_factory() as uow:
        s = uow.sessions.get(id) or raise_not_found(id)
        reset = s.reset(at=clock.now())
        uow.sessions.save(reset)
        uow.audit.record("reset", id, at=clock.now())
        uow.outbox.add(SessionResetEvent.from_(reset))
        uow.commit()
        return reset
```

All repository writes share one transaction. Outbox row written in the **same** transaction → at-least-once delivery without dual-write.

## Atomic Boundary

| Inside one UoW | Outside |
|---|---|
| Aggregate mutations | Returning DTOs to the API layer |
| Audit rows | Emails, push notifications |
| Outbox row | External HTTP calls |
| Cache invalidation messages (via outbox) | Direct cache writes |

External effects fire after commit, never inside.

## Outbox over Dual-Write

Persist event in the same UoW; a dispatcher publishes from the outbox. Failures retried with idempotency + backoff (skill:resilience-retries); consumers idempotent (skill:restful-http-design).

For jobs that span multiple requests or survive deploys, one UoW per step is not enough — use skill:pipeline-saga-orchestration.

## GOOD

```python
def transfer(uow_f, src: AccountId, dst: AccountId, amount: PositiveMoney) -> Receipt:
    with uow_f() as uow:
        a = uow.accounts.get(src) or raise_not_found(src)
        b = uow.accounts.get(dst) or raise_not_found(dst)
        a2, b2 = a.debit(amount), b.credit(amount)
        uow.accounts.save_all([a2, b2])
        uow.outbox.add(TransferCompleted(src, dst, amount))
        uow.commit()
        return Receipt.from_(a2, b2)
```

Two writes + one event in one transaction. Idempotent retry safe via outbox.

## BAD

```python
def transfer(src, dst, amount):
    a = db.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", amount, src)
    requests.post("https://notifications/api", json={"type": "debit"})
    b = db.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", amount, dst)
    return ok()
```

Dual-write. HTTP between two updates. Crash after `requests.post` → divergent state. No invariant. No rollback.

## Red Flags

- Two `commit`s in one use case.
- Side effect (email, webhook) fires inside `with uow:`.
- Repository takes a connection argument; caller threads it manually.
- Domain object calls `session.commit()` itself.
- Outbox bypassed because "this one is fine".
