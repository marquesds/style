---
id: agent-workflow
kind: rule
title: Agent Workflow
description: >
  Plan mode default. RPI (research, plan, implement) with one subagent per phase.
  Stop on drift. Subagents for exploration. Manual proof before done. Mandatory
  best-model review subagent on the diff before done. Bug report = root cause hunt,
  no hand-holding.
applies_when:
  - any task with 3+ steps
  - architectural decision
  - bug report
always_apply: true
globs: "**/*"
agents:
  claude: { kind: rule }
  cursor: { kind: rule, glob: "**/*" }
  codex:  { section: rules }
  goose:  { section: rules }
  openclaw: { section: rules }
  opencode: { kind: rule }
  pi:       { section: rules }
  vibe:   { kind: rule }
---

# Agent Workflow

Plan first, execute in small steps, and verify with proof.

## Plan Mode Default

Use plan mode for any task with 3+ steps or an architectural decision. If the work drifts, stop and replan before continuing.

An upfront spec cuts ambiguity. Use a cheap model for exploration (haiku, flash, composer-2), and reserve the expensive model for the edit.

## RPI: Research → Plan → Implement

Non-trivial work runs the RPI loop. The spec and phase gates come from skill:spec-driven-development (SPECIFY → PLAN → TASKS → IMPLEMENT). The main thread orchestrates and holds only compressed artifacts — **each phase runs in its own subagent**:

- **Research** → explore subagent(s). Gather context, return a summary, not file dumps.
- **Plan** → planning subagent. Produce the spec/plan per skill:spec-driven-development.
- **Implement** → implementation subagent(s). Execute task slices, one at a time.

Phase gates hold: the human confirms before the next phase starts (the same gate as `Ready-to-Code` below).

## Planning: Product + Requirements

Every implementation task starts by running **skill:requirements-crushing** before
non-markdown edits. Feature, fix, refactor, integration, UX, business rule, and
test work all pass through the gate. Trivial, unambiguous work may use the
skill's micro-brief; any open question upgrades it to the full brief.

Need **`Ready-to-Code: YES`** before code. If the brief has unanswered open
questions, stop the line: ask, recommend an answer, and do nothing else until
the human answers. Do not scaffold, edit the "safe parts", or proceed on silent
assumptions.

The only override is the human writing **`blind mode`** for the current task.
Then follow skill:requirements-crushing: record the AI-assumed answers and add
the required PR disclosure. Blind mode does not carry into the next task.

User-facing, cross-team, or high-impact → plan step **surfaces product-relevant
questions**: who affected, success metric, compliance, rollout, UX copy, edge
users. Pure engineering bugs still need autonomous root cause below, but the
brief captures why, reproduction, and the expected behavior before the fix.

Behavior / product / compliance uncertainty → questions belong **in planning**,
not ticket hand-holding disguised as "which line broke?".

**Staff+/owner lens.** In **plan mode**, planning output **must** include explicit **trade-offs** (we gain X / we pay Y—e.g. latency vs complexity, speed vs reversibility, build vs buy, scope vs timeline), not only a risk list, plus questions whose answers change whether the work is worth doing or how it is shaped:

- Worst realistic failure: who absorbs the downside (users, support, liability, brand)?
- Opportunity cost: next-best use of this effort?
- Irreversible decisions: blast radius, rollback, who owns the failure mode?
- Run rate or spend (infra, vendor, ops); $$ or SLA impact if we slip or guess wrong?
- Contractual or regulatory exposure; incident and support burden if we ship?

What would we measure to know we should revert?

## Stop The Line

If a test fails unexpectedly or the diff grows beyond scope, stop and replan. A half-fixed state is worse than no change.

## Subagents First

Spawn subagents when the triggers apply. Give each subagent one task so the main context stays clean. See skill:subagent-first for details.

## Verify Before Done

Never mark complete without proof. Run full test suite. Run lint. Run type check.

Manually exercise each changed user/operator-visible surface before "done". Happy path
plus relevant failure/edge path. Record exact steps + observed result in final response
and PR test plan. No record = not done.

Ask: would staff engineer approve?

Run the suite **in parallel** when safe (skill:tdd → Run Parallel When Safe). Serialize the offending tests, not the whole suite.

## Mandatory Review Subagent

After tests, lint, and types pass — and **before** marking complete — spawn a code-review subagent on the **best model available**. This is not optional: cheap models explore, the strongest model reviews (the dual of "reserve the expensive model for the edit").

The subagent reviews **only the new changes** (working diff or branch diff) using skill:code-review-and-quality — six axes, severity labels. Fix every `Critical` finding before done. Record the review outcome in the final response and PR.

No review subagent run = not done.

## Autonomous Bug Fixing

For a bug report, reproduce the failure, find the root cause, and propose the fix. Do not ask the user to choose between options that the code can answer.

## GOOD

```python
def reset_session(session_id: SessionId) -> Session:
    """Atomic reset; preserves audit log."""
    with unit_of_work() as uow:
        s = uow.sessions.get(session_id)
        s.reset(at=now())
        uow.audit.record("reset", session_id)
        return s
```

```bash
ruff check . && pytest && pyright
```

Manual proof: POST /sessions/{id}/reset succeeds twice; unknown session returns 404.
Verified all four. Done.

## BAD

```python
def reset_session(id):
    s = db.execute("SELECT * FROM sessions WHERE id = ?", id)
    s.reset_at = "2024-01-01"
    db.execute("UPDATE ...")
```

Untyped. Hardcoded date. No transaction. No audit. No tests. Pushed through without plan.

## Red Flags

- Edit 5 files before scoping work.
- RPI phase executed inline in the main thread.
- Implementation starts with no spec from skill:spec-driven-development.
- Skip tests because "small change".
- Ask user A-or-B when answer findable in code.
- Implement while the requirements brief still has unanswered questions.
- Assume answers without the human writing `blind mode`.
- Mark complete without running suite.
- Mark complete without recorded changed-surface manual proof.
- Mark complete without spawning the review subagent.
- Review run on a cheap model to save tokens.
