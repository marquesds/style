---
id: data-quality-and-analytics
kind: skill
title: Data Quality and Analytics
description: >
  Single canonical metric definitions, typed event schemas, declared lineage,
  versioned definition changes, and pipeline assertions. Product correctness,
  not telemetry observability.
applies_when:
  - adding a tracking event or product metric
  - building or reviewing an analytics dashboard
  - changing a metric definition
  - auditing data lineage from source to dashboard
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

# Data Quality and Analytics

One canonical definition per metric, owned in code. Schema validated at
the boundary. Lineage declared. Definition changes create a new series.

Distinct from skill:wide-events-and-cardinality (SLO telemetry). This skill
covers product/business correctness: the numbers stakeholders make decisions
from.

## Canonical Metric Definition

Every metric has one owner, one definition, stored in code — not buried in a
BI tool or a README no one reads:

```python
@dataclass(frozen=True)
class MetricDef:
    name: str
    description: str
    owner: str
    sql: str
    freshness_sla_hours: int
```

Name the metric in code exactly as it appears in dashboards. Divergence between
code name and BI name is a lineage break.

## Typed Event Schema at the Boundary

Reject malformed events at ingest. Never log silently and hope:

```python
class PurchaseEvent(BaseModel):
    user_id: UUID
    product_id: str
    amount_cents: int
    currency: str
    occurred_at: datetime
```

Pydantic/Zod/Avro — pick one. Schema validation failure → dead-letter queue +
alert, not silent null column. Cross-ref skill:defensive-programming for
boundary validation pattern.

## Lineage Declaration

Source table → transformation → mart → dashboard, declared in code or a
dbt-style manifest. Every hop is testable:

```
raw.purchase_events
  → stg.purchases        (parse, clean, dedupe)
  → mart.daily_revenue   (aggregate by day + currency)
  → dashboard.revenue    (time-series chart)
```

If a transformation is undocumented, it cannot be audited when numbers diverge.

## Definition-Change Protocol

Never silently re-shape an existing metric series. Stakeholders trust historical
consistency:

1. New metric name: `revenue_net_v2` alongside `revenue_net`.
2. Run both in parallel; validate they agree on known-good periods.
3. Migrate dashboards; deprecate old series per skill:deprecation-and-migration.
4. Delete old series after migration confirmed.

Changing the SQL under an existing name without versioning breaks every
historical comparison.

## Pipeline Assertions

Assert freshness, row-count ranges, and null thresholds in the pipeline, not
in post-hoc dashboard audits:

```python
def assert_pipeline_health(mart: Table) -> None:
    age_h = (now() - mart.max_updated_at).total_seconds() / 3600
    assert age_h < mart.freshness_sla_hours, f"stale: {age_h:.1f}h"
    assert mart.row_count > mart.min_expected_rows, "row count below floor"
    assert mart.null_rate("amount_cents") < 0.001, "null rate exceeds threshold"
```

## Dashboard Cross-Check Before Launch

Before a dashboard goes live, cross-check aggregate totals against the
source-of-truth system (e.g., payment processor report, order DB count).
Discrepancy > 1% blocks launch until reconciled.

## GOOD

```python
DAILY_REVENUE = MetricDef(
    name="daily_revenue_usd",
    description="Net revenue in USD settled on the calendar day, FX at close.",
    owner="data-platform",
    sql="SELECT date, SUM(amount_usd) FROM mart.purchases GROUP BY 1",
    freshness_sla_hours=2,
)
```

Named, owned, SQL visible, SLA declared, definition in version control.

## BAD

```python
# BI tool query, saved as "Revenue (new)" by analyst
# SELECT date, SUM(amt) FROM purchases WHERE flag = 1
# Nobody knows what flag=1 means or when it changed
```

Definition lives in a BI tool. Owner unknown. Flag meaning undocumented.
Change history lost. Cannot be tested.

## Red Flags

- Metric defined only inside a BI tool; no code owner.
- Event schema is `dict[str, Any]`; nulls discovered weeks later.
- SQL changed under an existing metric name with no versioning.
- Pipeline has no freshness or row-count assertion.
- Dashboard launched without cross-check against source of truth.
- "Revenue" means different things in two dashboards; no canonical def.
- Lineage undocumented; impossible to trace a number back to raw events.
