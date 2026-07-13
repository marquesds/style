---
id: adr-writing
kind: skill
title: ADR Writing
description: >
  Create or update ADRs for architecture decisions using the SMART + STAR ADR
  format. Use for decisions that outlive a single PR: service boundaries,
  provider strategy, storage/retention choices, rollout architecture, tenancy
  model, or any decision with material trade-offs.
applies_when:
  - creating or updating an ADR for an architecture decision
  - a decision has material trade-offs that outlive a single PR
  - writing an ADR using the SMART + STAR format
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

# ADR Writing

Use for architecture decisions that outlive a single PR: service boundaries,
provider strategy, storage/retention choices, rollout architecture, tenancy
model, or any decision with material trade-offs.

This skill depends on `context-gathering` and `requirements-crushing`.
Do not draft from memory. Gather evidence first, then crush requirements into a
Ready-to-Decide brief, then write the ADR from that evidence.

Format follows the STAR/SMART ADR pattern from
`msfidelis/staff-plus-star-method-ards` (`template/ADR-STAR.md`).

## File Location

```text
docs/adr/NNNN-kebab-title.md
```

If the project has no `docs/adr/` yet, create it with a short `README.md` index.
Do not bury ADRs in `.specs/`; specs can reference ADRs, but ADRs are durable
project documentation.

## Required Inputs

Before writing the ADR, run:

1. `context-gathering` to collect repo docs/code, Linear, Datadog, Notion, Slack,
   and Git/GitHub context when available.
2. `requirements-crushing` to produce a concise brief with Why, scope,
   constraints, success metrics, rollout, rollback, tests, and open questions.

The ADR must be filled from those inputs. If a field cannot be filled, write
`TBD` only while status is `Proposed`, and include the exact missing evidence
needed to graduate to `Accepted`.

Minimum evidence to collect:

- Current code path and owning modules/packages.
- Existing docs/runbooks/secrets that will drift if the decision lands.
- Baseline metrics or an explicit measurement plan.
- Known incidents, product asks, or stakeholder context.
- Privacy, tenant isolation, provider, cost, and operability constraints.
- Alternatives already tried or rejected.

## Required Frontmatter

```yaml
---
id: ADR-YYYY-NNN
title: "<decision title>"
status: Proposed | Accepted | Rejected | Obsolete
authors: [<names>]
date: YYYY-MM-DD
subsystem: [<owning subsystems>]
related: [Linear-..., RFC#..., ADR-..., PR#..., Datadog-...]
tags: [<relevant tags>]
---
```

Use `Proposed` while discussing. Use `Accepted` only after human approval. Keep
obsolete/superseded ADRs as history; do not rewrite past decisions to hide churn.

## Required Body Sections

1. **Context** — current situation, why change is needed now. Include audience,
   symptoms, current topology, baseline metrics (p95/p99, incidents, SLO, cost
   with window and source), and constraints (privacy, tenancy, budget, compliance).
2. **Objective — SMART (Task)** — specific, measurable, achievable, relevant,
   time-bound goals: behavior, latency/reliability, privacy/isolation, blast
   radius, cost, measurement plan.
3. **Decision** — state the decision. Include a small Mermaid diagram when it
   clarifies the data/control flow.
4. **Alternatives Considered** — each alternative and why rejected.
5. **Consequences** — positive and negative (trade-offs, debt, operational burden).
6. **Implementation And Rollout Plan** — steps plus rollback.
7. **Success Metrics And Observability** — RED metrics, boundary spans,
   privacy/tenant checks, provider health, minimum alerts.
8. **Results — STAR** — Situation (before baseline), Task (SMART goals),
   Action (what was done), Result (after-window deltas, side effects, follow-up).

## Rules

- Cite evidence. Use Datadog/Linear/Slack/Notion/repo links when available.
- Every major field must trace back to gathered context or the requirements brief.
- Baseline metrics can be `TBD` only while status is `Proposed`; `Accepted` ADRs need a measurement plan at minimum.
- Do not set status to `Accepted` while unresolved questions remain in the requirements brief.
- Every ADR must name trade-offs, rollout, rollback, and observability.
- Privacy/tenancy decisions must call out who can access sensitive data and how cross-tenant access is prevented.

## GOOD

ADR for "move WebSocket runtime out of the monolith into a dedicated service"
cites the current p95 latency from Datadog, the related incident link, the
Linear issue, and the Slack decision thread. The brief was crushed first.
Trade-offs, rollout, rollback, and observability are all filled. Status is
`Proposed` until human approval.

## BAD

ADR drafted from memory with `TBD` in every baseline field, no evidence links,
no alternatives, and status set to `Accepted` by the agent. The decision cannot
be reviewed because there is nothing to check against.

## Red Flags

- ADR written from memory without `context-gathering` and `requirements-crushing`.
- Status set to `Accepted` without human approval or while questions remain.
- No alternatives considered.
- No trade-offs, rollback, or observability section.
- Privacy/tenancy decision that does not call out access and isolation.
- ADR buried in `.specs/` instead of `docs/adr/`.
