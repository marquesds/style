---
id: spec-driven-development
kind: skill
title: Spec-Driven Development
description: >
  Create designs and specifications before code. Surface assumptions early.
  Gated workflow: SPECIFY → PLAN → TASKS → IMPLEMENT.
applies_when:
  - creating or updating a design or technical specification
  - writing a clear standalone implementation plan
  - new feature or module
  - change touches multiple files
  - architectural decision pending
  - requirements ambiguous
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

# Spec-Driven Development

Code without a spec is guessing. Write the spec first and keep gates between phases.

## Workflow

```text
SPECIFY → PLAN → TASKS → IMPLEMENT
   ↑         ↑       ↑         ↑
 human    human   human     execute
review   review  review
```

Each gate: human confirms before next phase starts.

## Behavioral Modeling Protocol

Every PR review, design/spec creation, test-design or behavior-test task, and
every individual TDD cycle starts with a logical behavioral analysis. No
trivial/stateless exemption. Describe scope, assumptions, observables, initial
state, transitions, accepted traces, forbidden traces, and invariants. Classify
every observable behavior as Added, Removed, Changed, or Unchanged in every
workflow, not only reviews.

Create one collision-safe invocation directory:

```text
~/.style/specs/quint/<project>/<workflow>/<task-id>/<invocation-id>/
```

`workflow` is `review`, `spec`, `test`, or `tdd`. Sanitize user-derived path
segments; include timestamp plus random/unique suffix in `invocation-id`. Never
overwrite an invocation. To reuse a model, copy it into a fresh invocation.
Keep only synthetic/redacted data: no PII, secrets, or production payloads.

Each invocation records concise local evidence:

- `manifest.md`: task/scope, assumptions, observables, tool version, module,
  seed, bounds, backend, invariant/test names, and exact commands.
- `logical-analysis.md`: states, transitions, accepted/forbidden traces, and
  expected behavioral delta.
- `model.qnt`; review uses both `before.qnt` and `after.qnt`.
- `typecheck.log`, `run.log`, `test.log`, `result.md`, `tool-error.log` when
  applicable, and ITF traces where Quint produces them.

### Quint lifecycle

1. Run `command -v quint` for every invocation.
2. Missing: record logical-only fallback in `result.md`; continue logically.
3. Found: record `quint --version`, then typecheck, simulate, and test every
   model. Use installed help as authority. These commands match Quint 0.32.0:

```bash
quint typecheck model.qnt
quint run model.qnt --main Model --init init --step step \
  --invariants invariantName --witnesses witnessName --max-steps 20 \
  --max-samples 100 --seed 0x5eed --backend rust --n-threads 1 \
  --out-itf 'run_{seq}.itf.json'
quint test model.qnt --main Model --match '^test_' \
  --max-samples 100 --seed 0x5eed --backend rust \
  --out-itf 'test_{test}_{seq}.itf.json'
```

`typecheck` accepts only its input plus output options. Do not pass run-only
flags (`--init`, `--step`, `--invariants`, `--witnesses`, `--max-steps`, or
`--n-threads`) to `quint test`. Always pair `--seed` with explicit
`--max-samples`.

On every failed Quint attempt, immediately append exact command, exit status,
and stderr to `tool-error.log`, and reference that failure in `result.md` even
if a corrected retry later succeeds. Inspect and correct model/command once.
If retry still fails, continue with explicit logical fallback. Never silently
downgrade.

Simulation is bounded evidence, not proof that implementation matches model.
Zero sampled witnesses do not prove impossibility. Humans decide whether a
behavioral delta is intended. This protocol excludes `verify`, MBT,
QuintConnect, CI integration, new dependencies, and production instrumentation.

## Phase 1: SPECIFY

Vague or high-impact ask → **skill:requirements-crushing** first (brief + Ready-to-Code gate); avoids bloating this phase with full crush template here.

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

Reframe vague asks into measurable outcomes: latency bounds, invariant
preservation, accepted traces, and forbidden traces.

## Phase 2: PLAN

Modules, types, ports, dependencies, order, risks. Prose + diagram if useful.

**Complex change → tech spec.** Cross-module work, schema change, new external
boundary, new dependency, or a decision that locks in a trade-off → write a
tech spec: problem, options considered, choice + reasoning, blast radius,
rollback. Single accepted decisions land as ADRs under `docs/adr/`
(see rule:documentation). For a one-pager system overview, see
skill:architecture-haiku.

## Phase 3: TASKS

Slice into discrete units. Each: testable, independently mergeable, < 1 day. Order them.

Each task follows skill:task-definition: verb-led title, single estimate scale
(T-shirt or Fibonacci, no mixing), acceptance criteria in Gherkin. `> XL` or
`> 13` → slice smaller before writing.

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

## Behavioral contract
- Added: reset transitions stuck → active and writes one audit row.
- Forbidden: reset without audit; reset mutating an unrelated session.
- Invariant: session and audit commit atomically.
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
