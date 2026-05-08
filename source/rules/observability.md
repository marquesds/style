---
id: observability
kind: rule
title: Observability
description: >
  Three pillars: logs, traces, metrics. Correlation IDs everywhere.
  Log at state changes. No PII in logs. Tooling-agnostic.
applies_when:
  - any state change
  - any external boundary call
  - any error path
always_apply: true
globs: "**/*"
agents:
  claude: { kind: rule }
  cursor: { kind: rule, glob: "**/*" }
  codex:  { section: rules }
  vibe:   { kind: rule }
---

# Observability

Cannot fix what you cannot see. Three pillars + correlation.

## Three Pillars

| Pillar | Use for |
|---|---|
| Logs (structured) | discrete events, errors, state transitions |
| Traces | request paths, latency hotspots, fan-out |
| Metrics | rates, durations, saturation, error counts |

JSON logs. Span per external boundary. Counters + histograms for SLOs.

## Correlation

Every request → correlation id (trace id, request id, session id). Propagate through async boundaries. Log it on every line.

## Log At State Changes

Persist, publish, change auth, fail validation, retry → log. Quiet in steady state. Loud at transitions.

## No PII

No emails, names, raw tokens, payment data in logs. Hash or redact.

## Boundary Spans

Every DB query, HTTP call, queue publish, cache miss → span. Tag with operation + outcome. Trace tells story without log diving.

## SLO-Worthy Metrics

Rate, errors, duration (RED). Saturation. Per-endpoint, per-job. Alert on derivatives, not absolutes.

## GOOD

```python
log = structlog.get_logger()

async def reset_session(session_id: SessionId) -> Session:
    log.info("session.reset.start", session_id=str(session_id))
    with tracer.start_as_current_span("reset_session") as span:
        span.set_attribute("session.id", str(session_id))
        s = await sessions.reset(session_id)
        sessions_reset_total.inc()
        log.info("session.reset.ok", session_id=str(session_id))
        return s
```

## BAD

```python
def reset_session(id):
    print(f"resetting {id}")  # plain print, no fields
    s = sessions.reset(id)
    print("ok")
    return s
```

`print` not structured. No correlation. No trace. No metric. Untraceable in prod.

## Red Flags

- Errors caught silently, logged at info level (or not at all).
- PII in log fields.
- One blob log message instead of structured fields.
- New endpoint shipped without span + counter.
- Alerts on raw counts (noisy) instead of rates.
