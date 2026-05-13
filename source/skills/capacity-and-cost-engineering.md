---
id: capacity-and-cost-engineering
kind: skill
title: Capacity and Cost Engineering
description: >
  Capacity models, pre-launch load tests, per-service cost guardrails, and
  right-sizing loops. Distinct from per-request rate limiting and post-hoc
  spend observability.
applies_when:
  - sizing infrastructure for a launch or peak event
  - planning capacity for expected traffic growth
  - setting up cost budgets or guardrails
  - running a load test before shipping
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

# Capacity and Cost Engineering

Model before you launch. Test under load. Guard spend. Right-size after
steady state. Degrade gracefully before saturation.

Distinct from skill:rate-limiting-and-throttling (per-request gate) and from
skill:wide-events-and-cardinality (post-hoc spend visibility).

## Capacity Model

Before provisioning, fill in the formula:

```
peak_rps × p99_latency_s × parallelism_factor ≤ instance_count × throughput_per_instance
```

Headroom rules of thumb:

| Traffic type | Headroom multiplier |
|---|---|
| Steady-state daily peak | 2× |
| Launch / campaign spike | 5× |
| Batch job burst | 3× |

```python
def required_instances(
    peak_rps: float,
    throughput_per_instance: float,
    headroom: float = 2.0,
) -> int:
    import math
    return math.ceil((peak_rps / throughput_per_instance) * headroom)
```

## Load Test Discipline

Run a load test before every significant launch and when throughput risk
changes:

- Ramp profile mirrors real traffic shape (not vertical step function).
- Warm-up phase to fill caches before measuring.
- Measure p50, p95, p99 latency + error rate at target peak + 2× peak.
- Failure criterion: error rate > 0.1% or p99 > SLO budget.

Tools: k6, Locust, or Artillery — pick the one already in the repo.
Cross-ref skill:resilience-retries — retry storms under load inflate cost.

## Cost Guardrails

Every service and environment has a budget alert:

```python
@dataclass
class CostGuardrail:
    service: str
    env: str
    daily_budget_usd: float
    anomaly_threshold_pct: float = 0.30
    hard_kill: bool = False
```

- Alert fires at `anomaly_threshold_pct` above trailing 7-day average.
- `hard_kill=True` for runaway batch jobs (disable trigger, not the service).
- LLM token spend attributed per feature flag or product line
  (skill:llm-system-design token budgeting).

## Cost-per-Feature Accounting

Tag cloud spend by feature: cloud resource labels + LLM token attribution.
Weekly cost-per-feature report catches unintended spend before it compounds.

## Right-Sizing Loop

After steady state (≥2 weeks of prod traffic):

1. Pull CPU and memory utilization percentiles per instance type.
2. Downsize when p95 CPU < 40% and p95 memory < 50% for two weeks.
3. Re-run load test at new size before committing.
4. Document new sizing in infra-as-code, not only in the cloud console.

## Graceful Degradation Under Load

When approaching saturation, degrade in ranked order before shedding:

1. Return cached / slightly stale response.
2. Reduce response precision (summarize instead of full detail).
3. Return 503 with `Retry-After` — skill:rate-limiting-and-throttling for
   the 429/503 semantics.

Never silently queue unbounded work — that turns a capacity event into a
data-loss or OOM incident.

## GOOD

```python
# Load test gate in CI/CD
def check_load_test_result(report: LoadReport) -> None:
    assert report.error_rate < 0.001, f"error rate {report.error_rate:.1%}"
    assert report.p99_ms < 500, f"p99 {report.p99_ms}ms exceeds SLO"
```

Objective pass/fail criteria enforced before promotion to prod.

## BAD

```python
# Provisioning by feel
replicas = 3  # "seemed like enough last time"
```

No model, no test, no guardrail. First peak event reveals the gap.

## Red Flags

- Provisioning based on gut feel with no capacity model.
- Load test run post-launch ("we'll test it live").
- No cost alert; bill reviewed only at month end.
- LLM token cost unattributed; whole org charged to a single line item.
- Right-sizing never revisited after initial launch.
- Under-load behavior is crash or timeout, not graceful degradation.
- Retry storms not modeled as multipliers on peak load.
