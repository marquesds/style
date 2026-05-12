---
id: wide-events-and-cardinality
kind: skill
title: Wide Events + Cardinality
description: >
  One wide structured event per request. High cardinality on event fields is a
  feature; high cardinality on metric labels is expensive. SLOs from event counts.
  Tail-based sampling for slow or failing traces.
applies_when:
  - designing instrumentation for a new service
  - debugging unknown unknowns in production
  - setting up SLOs and error budgets
  - choosing between structured logs, traces, and metrics
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

# Wide Events + Cardinality

One event per request, wide enough to answer any question. Metrics stay narrow.

## Wide Structured Events

One event per request (or job) accumulates **all relevant context** before emit:

```python
event = {
    "trace_id":   span.trace_id,
    "user_id":    request.user_id,
    "tenant_id":  request.tenant_id,
    "route":      request.path,
    "status":     response.status_code,
    "latency_ms": elapsed_ms,
    "db_time_ms": db_span.duration_ms,
    "cache_hit":  cache.hit,
    "flags_eval": flags.evaluated,
    "service":    SERVICE,
    "version":    VERSION,
    "region":     REGION,
}
emit(event)
```

Debugging unknown-unknowns: filter on any dimension, group by the next, repeat.
No pre-built dashboard needed — the event store answers arbitrary queries.

Grounded in Majors / Fong-Jones / Miranda, *Observability Engineering* (O'Reilly 2022).

## Cardinality: Two Contexts

| Context | High cardinality | Verdict |
|---|---|---|
| Event store (Honeycomb, ClickHouse, wide-log) | `user_id`, `trace_id`, `request_id` | **Feature** — query freely |
| Metric labels (Prometheus, Datadog, StatsD) | `user_id` on a counter | **Expensive** — avoid |

They are different tools with different cardinality budgets. Don't conflate.

Metric labels: use low-cardinality dimensions (`route`, `status_class`, `region`).
Reserve `user_id`-level detail for the event store.

## Three Pillars vs Wide Events

Three pillars (logs, traces, metrics) are useful primitives. Modern stance:

- **Wide events** as primary artifact. One event per request beats scattered log lines.
- **Traces** are a structured view over events, correlated by `trace_id`.
- **Metrics** are aggregates derived from events, used for alerting at scale.

Don't replace metrics with events for alerting — metrics are cheaper to query at
rule-evaluation time. Add wide events **alongside** to answer "why is the rate high?".
See rule:observability for structured logging requirements.

## SLOs + Error Budgets

SLI = good events / total events over a rolling window.

```text
SLI: requests where latency_ms < 200 AND status < 500
SLO: SLI >= 99.9% over 30 days
Error budget: 43.2 minutes of bad requests per 30 days
```

Alert on **burn rate**, not raw error count:

```text
burn rate > 14.4× for 5 min  →  page (consumes 1 h of budget)
burn rate >  1×   for 1 h    →  ticket (slow leak)
```

## Sampling

| Strategy | Use |
|---|---|
| **Head-based** | Decide at trace start; simple; misses rare errors |
| **Tail-based** | Decide after span completes; keep all errors + slow tails |
| **Dynamic** | Downsample high-volume healthy traffic; keep 100% of anomalies |

Always keep: errors, slow outliers (>p99), traces matching an active investigation.
Never drop: the first occurrence of a new error type.

## Bubble-Up Debugging

```text
1. Filter: trace_id = "abc123"  → full request timeline
2. Filter: status = 500, region = "us-east-1"  → narrow the population
3. Group by: route  → one route dominates
4. Group by: version  → new deploy correlates
5. Drill: filter version = "2.1.4"  → specific DB query is slow
```

Each group-by is a dimension on the wide event. Pre-built dashboards become
optional; the event store answers the question directly.

## GOOD

Single `emit(event)` at request end with context accumulated during handling.
Prometheus counter uses `route` + `status_class` labels only. SLO alert fires on
burn rate. Tail sampler keeps all 5xx. See skill:n-plus-one-prevention for `db_time_ms`.
See skill:resilience-retries for `circuit_state` field on the event.
See skill:queue-topology-design for `queue_depth` on consumer events.

## BAD

```python
log.info("request received")
log.info(f"user {user_id} found")
log.info("db query done")
log.info("response sent", status=200)
```

Four scattered lines per request. No single queryable object. No `latency_ms` field.
Signal is fragmentary; debugging requires stitching lines by timestamp.

## Red Flags

- Prometheus label includes `user_id` or `order_id` — cardinality explosion.
- SLO alert fires on raw error count (noisy at low traffic).
- No `trace_id` field on structured log lines.
- Debugging requires joining four separate log streams.
- Sampler drops all errors to reduce cost.
- No `latency_ms` or equivalent on the primary event.
- `emit(event)` called at the start of a request instead of the end.
