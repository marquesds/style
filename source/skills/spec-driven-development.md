---
id: spec-driven-development
kind: skill
title: Spec-Driven Development
description: >
  Spec before code. Surface assumptions early. Gated workflow:
  SPECIFY → PLAN → TASKS → IMPLEMENT.
applies_when:
  - new feature or module
  - change touches multiple files
  - architectural decision pending
  - requirements ambiguous
agents:
  claude: { kind: skill }
  cursor: { kind: rule }
  codex:  { section: skills }
  vibe:   { kind: skill }
---

# Spec-Driven Development

Code without spec = guessing. Spec first. Gates between phases.

## Workflow

```text
SPECIFY → PLAN → TASKS → IMPLEMENT
   ↑         ↑       ↑         ↑
 human    human   human     execute
review   review  review
```

Each gate: human confirms before next phase starts.

## Phase 1: SPECIFY

Surface assumptions immediately:

```text
ASSUMPTIONS:
1. Async runtime (asyncio).
2. Storage TBD; in-memory port for now.
3. AuthN at the gateway, not in app.
→ Correct now or I proceed.
```

Six-area template:

| Area | Content |
|---|---|
| Objective | What, why, who, success criteria |
| Commands | Build, test, run, lint, type check |
| Structure | Modules, ports, types to add or change |
| Code style | One real snippet showing the pattern |
| Testing strategy | Unit vs integration split, fixtures, property tests |
| Boundaries | Always / Ask first / Never |

Reframe vague asks:

```text
ASK: "make ingest faster"
SUCCESS:
  - p50 single ingest < 1ms (benchmark X)
  - batch 100 < 50ms
  - no allocation in hot path
→ Right targets?
```

## Phase 2: PLAN

Modules, types, ports, dependencies, order, risks. Prose + diagram if useful.

## Phase 3: TASKS

Slice into discrete units. Each: testable, independently mergeable, < 1 day. Order them.

## Phase 4: IMPLEMENT

One task at a time. TDD per task. Update spec when reality diverges.

## GOOD

```markdown
# Spec: Session Reset

## Objective
Ops engineers can reset a stuck session without dropping audit trail.
Success: reset latency p99 < 50ms; audit row written 100% of resets.

## Boundaries
- Always: write audit row in same UoW as reset.
- Ask first: schema change, new port, public API addition.
- Never: skip the audit row, mutate sessions outside UoW.
```

## BAD

```markdown
# Session Reset

Add a reset button. Make it work. Probably wire it through Sessions.
```

Vague. No success criteria. No boundaries. No commands. Recipe for sprawl.

## Red Flags

- Implementation starts before assumptions are written down.
- "Spec" is two lines and zero acceptance criteria.
- Decisions made silently mid-implementation, never folded back into the spec.
- Spec written **after** the code (that's documentation, not specification).
