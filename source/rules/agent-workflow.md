---
id: agent-workflow
kind: rule
title: Agent Workflow
description: >
  Plan mode default. Stop on drift. Subagents for exploration. Verify before done.
  Bug report = root cause hunt, no hand-holding.
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
  vibe:   { kind: rule }
---

# Agent Workflow

Plan first. Execute small. Verify hard.

## Plan Mode Default

Task 3+ steps OR architectural decision → plan mode. Goes sideways → STOP, replan. No pushing through.

Spec upfront cuts ambiguity. Cheap model for exploration (haiku, flash, composer-2). Expensive model for the actual edit.

## Stop The Line

Test fails unexpectedly → stop. Diff bigger than expected → stop. Re-plan immediately. Half-fixed state worse than zero state.

## Subagents First

Spawn liberally. One task per subagent. Main context stays clean. See skill:subagent-first for triggers.

## Verify Before Done

Never mark complete without proof. Run full test suite. Run lint. Run type check. Ask: would staff engineer approve?

## Autonomous Bug Fixing

Bug report → reproduce → fix root cause. No "should I do A or B?" questions. Find answer yourself, then propose fix.

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

Verified all three. Done.

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
- Skip tests because "small change".
- Ask user A-or-B when answer findable in code.
- Mark complete without running suite.
