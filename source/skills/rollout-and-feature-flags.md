---
id: rollout-and-feature-flags
kind: skill
title: Rollout + Feature Flags
description: >
  Four flag archetypes, progressive delivery, flag debt with removal date,
  flag vs config distinction, automated rollback signals tied to SLO burn.
applies_when:
  - shipping risky or partial changes
  - gradual rollout or canary release
  - A/B experiment
  - ops kill-switch needed
  - flag cleanup or audit
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

# Rollout + Feature Flags

Ship dark. Light gradually. Kill fast. Remove the switch.

## Four Flag Archetypes

| Archetype | Purpose | Typical lifetime |
|---|---|---|
| **Kill-switch** | Disable broken feature without a deploy | Until stable; remove next sprint |
| **Gradual rollout** | 1% → 10% → 50% → 100% of traffic | Days to weeks |
| **Experiment (A/B)** | Compare two variants against a metric | Duration of experiment |
| **Ops toggle** | Enable costly operation (batch job, migration) on demand | Until removed post-run |

Every flag gets: owner, creation date, **removal date**, and a tracking issue.

## Flag ≠ Config

| Flags | Config |
|---|---|
| On/off or small variant set | Numeric tuning (timeouts, limits, thresholds) |
| Change frequently; removed when stable | Long-lived; part of deployment contract |
| Evaluated at runtime against a population | Injected from env or config service |
| Accrues debt if not removed | Stable operational concern |

Don't store gradual-rollout percentages as flags — that's config. Don't store
per-environment DB URLs as flags — that's config. The distinction matters for
lifecycle management and for audit trails.

## Progressive Delivery

1. **Canary**: route a small slice of traffic to the new version. Monitor error rate
   and p99. Promote or roll back based on SLO signal, not elapsed time.
2. **Ring** (internal → beta → general): staged user population expansion. Each ring
   needs an explicit go/no-go decision point before the next ring opens.
3. **Blue-green**: two live environments; instant traffic switch with instant rollback.

Gate promotion to the next ring on the SLO burn rate, not on a calendar.
See skill:wide-events-and-cardinality for measuring error rate at low traffic volumes.

## Flag Debt

Flags past their removal date are liabilities: dead branches in logic, extra test
surface, cognitive load.

Enforcement:

- Removal date in a registry (code annotation, feature-flag platform, or issue label).
- Stale flag = P2 tech debt. Assigned to the owner. See skill:deprecation-and-migration.
- CI can fail on flags past removal date if the registry supports it.

```python
@flag(name="new_checkout", remove_by="2026-07-01", owner="team-payments")
def new_checkout_enabled(request: Request) -> bool: ...
```

## Automated Rollback Signals

Define an SLO burn-rate threshold that triggers automatic kill-switch flip:

```text
error_rate > 1% for 5 min on /checkout → flip new_checkout = False
```

Wire the signal to your observability stack (rule:observability). Rollback must be
faster than on-call response time. Human confirmation required for rollforward.

## GOOD

Flag with owner + removal date + tracking issue. SLO-wired kill-switch ready before
rollout starts. Removal PR merged the sprint after the flag reached 100%.

## BAD

```python
if os.environ.get("ENABLE_NEW_FEATURE") == "true":  # added 2024-01-01, never removed
    ...
```

No owner. No removal date. Became permanent config. Logic fork maintained indefinitely.

## Red Flags

- Flag with no removal date in the registry.
- Feature flag "stable" for six months but never cleaned up.
- Rollout scheduled by calendar, not by SLO burn signal.
- Flag evaluated deep in the domain core instead of at the driving edge.
- More than ~10 active flags in a single service — audit overdue.
- Flag used to store per-environment credentials (that is config, not a flag).
