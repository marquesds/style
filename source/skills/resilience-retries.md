---
id: resilience-retries
kind: skill
title: Resilience — Retries, Idempotency, Breakers
description: >
  Retries only with idempotency or dedupe. Capped exponential backoff + jitter.
  Circuit breaker when downstream is unhealthy. Observability on attempts and
  breaker state.
applies_when:
  - outbound HTTP or RPC with failures
  - worker retries or pollers
  - designing idempotent handlers
  - thundering herd or cascade risk
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

# Resilience — Retries, Idempotency, Breakers

Retry **only** what is safe to repeat. Backoff **always** jitters. Fail fast when dependency is toast.

## Idempotency + Dedupe

At-least-once delivery ⇒ handler must be **idempotent** or **deduplicated** (natural key, idempotency key, outbox consumer ledger). Non-idempotent POST without key → **no blind retry**. See skill:restful-http-design, skill:unit-of-work-and-transactions (outbox + idempotent consumers).

## Exponential Backoff + Jitter

**Capped** exponential delay between attempts. **Jitter** (e.g. full jitter in `[0, min(cap, base * 2**k)]`) so retries don’t align. Hard **max attempts** and **max delay**. Classify errors: retry **transient** only; fail fast on 4xx you own, auth, validation.

## Circuit Breaker

After **N** failures (or error rate), **open**: short-circuit calls, surface healthy error upstream. **Half-open** probe after cool-down. **Close** on success. Emit **logs/metrics** on state change (see observability rule).

For worker-level isolation — queue splitting, per-queue concurrency limits, stale-job reapers — see skill:queue-topology-design.

## GOOD

```python
from random import uniform
from time import sleep


def with_retries(op, max_n=5, base=0.1, cap=30.0):
    for i in range(max_n):
        try:
            return op()
        except TransientError:
            if i == max_n - 1:
                raise
            lim = min(cap, base * 2**i)
            sleep(uniform(0, lim))
```

Idempotent `PUT` / keyed `POST` + policy above + breaker wrapper that increments `dependency_failures` and flips `circuit_open` with a structured log. Caps stop runaway.

## BAD

```python
def pay(client, payload):
    while True:
        try:
            return client.post("/v1/payments", json=payload)
        except Exception:
            sleep(1.0)
```

No idempotency key on **POST** — duplicates money. **Fixed** sleep, **no** jitter, **infinite** loop, retries **all** errors. No breaker — keeps hammering dead dependency; megaphones outage.

## Red Flags

- `for i in range(3): sleep(1)` on writes without dedupe.
- Retry `4xx` or validation errors.
- Same delay every attempt (herd).
- Breaker state invisible in metrics/logs.
