---
id: architecture-haiku
kind: skill
title: Architecture Haiku
description: >
  Single-page living architecture overview. Required sections include quality
  attributes in explicit priority order. Updated when architecture shifts, not
  when features ship. Distinct from a feature spec or a single-decision ADR.
applies_when:
  - onboarding new engineers to the system
  - architecture review or trade-off discussion
  - system-level decision about constraints or quality goals
  - existing haiku is stale after a significant shift
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

# Architecture Haiku

One page. Living. Prioritized. Not a feature spec, not an ADR.

## What It Is (and Is Not)

| Document | Scope | Update trigger |
|---|---|---|
| Architecture Haiku | System-level overview | Architecture shifts |
| Feature spec | One capability | Feature work (skill:spec-driven-development) |
| ADR | One decision | When that decision is made |

The haiku answers: "What is this system, what does it optimize for, and why is
it shaped the way it is?" — in one readable page.

## Required Sections

1. **Objective** — 2–3 bullets: what problem, for whom, success signal.
2. **Functional Requirements** — key capabilities the system must deliver.
3. **Technical Constraints** — non-negotiables (runtime, compliance, existing infra).
4. **Quality Attributes — in priority order** — ranked list; the order is the
   decision. Trade-offs follow from it.
5. **Design Decisions** — major choices driven by the quality attributes above.
6. **Future Plans** — known evolution; what is deliberately deferred.

## Quality Attributes Must Be Ranked

Listing attributes without rank is not a decision — it is a wish list.
The rank resolves trade-offs: when correctness and throughput conflict, which
wins? The haiku must answer.

Example rank:

```
1. Correctness (data must not be lost or corrupted)
2. Operability (on-call can diagnose and recover without author)
3. Throughput (sustain peak ingestion rate)
4. Latency (best-effort; degrade gracefully)
```

## Update Triggers

Update the haiku when:
- A quality attribute changes rank.
- A new hard constraint is introduced.
- A major design decision is made that the haiku does not reflect.

Do **not** update for individual feature additions. Features live in specs and
ADRs; the haiku reflects the shape of the whole.

## GOOD

```markdown
## Quality Attributes (priority order)
1. Correctness — audit trail complete; no silent data loss
2. Operability — p99 alert → runbook → resolved without author
3. Throughput — sustain 10k events/s at p95 < 200ms
4. Cost — cloud spend scales sub-linearly with volume
```

Priority is explicit. Trade-off is clear: correctness beats throughput when
they conflict.

## BAD

```markdown
## Quality Attributes
- Performance
- Reliability
- Scalability
- Security
- Maintainability
```

No rank. No metrics. Every attribute equal = none actionable. "Scalability"
conflicts with "Maintainability" constantly; no order means no resolution.

## Red Flags

- Quality attributes listed without a priority order.
- Haiku not updated after a major architectural shift.
- Document exceeds one page — it has become a spec.
- Objective has no success signal; team cannot tell if system is working.
- Design Decisions section missing or empty — rationale is oral tradition only.
