---
id: bug-first-debugging
kind: skill
title: Bug-First Debugging
description: >
  Never fix first. Reproduce as failing test, then fix. Regression test stays
  forever. Find root cause, not symptom.
applies_when:
  - bug report
  - failing test
  - unexpected behavior
  - production incident
agents:
  claude: { kind: skill }
  cursor: { kind: rule }
  codex:  { section: skills }
  goose:  { section: skills }
  openclaw: { section: skills }
  opencode: { kind: skill }
  pi:       { section: skills }
  vibe:   { kind: skill }
---

# Bug-First Debugging

Reproduce first. Fix second. Guard with regression test forever.

## Stop-The-Line

1. Stop adding features.
2. Preserve evidence: error output, logs, repro steps.
3. Diagnose via triage checklist.
4. Fix root cause.
5. Guard with regression test.
6. Resume after suite green.

## Triage Checklist

| Step | Action |
|---|---|
| Reproduce | Minimal repro. Fails locally. Same error string. |
| Localize | Which layer? Pure logic? Adapter? Boundary? Test itself? |
| Reduce | Strip case to smallest input that fails. |
| Root cause | Ask "why?" until structural reason found. |
| Test | Failing test that pins the bug. |
| Verify | Full suite + lint + types green. |

## Regression Tests

Colocated with feature tests. Tagged `@regression`. Name = expected behavior, not bug ID. Link issue / incident in docstring.

## Symptom vs Root Cause

```python
val = risky_call()                         # bug raises
val = risky_call() or default_value        # symptom fix; hides cause

try:
    val = risky_call()
except RiskyError as e:
    log.error("risky_call failed", exc_info=e)
    raise AppError.internal() from e        # root cause: handle + surface
```

## GOOD

```python
@pytest.mark.regression
def test_completing_session_sets_completed_at():
    """Bug INC-4221: completed_at stayed None after complete()."""
    store = MemoryStore()
    s = store.create(default_attrs())
    completed = store.complete(s.id)
    assert completed.status is Status.COMPLETED
    assert completed.completed_at is not None
```

Test pins behavior. Name describes outcome. Tag persists for grep.

## BAD

```python
def test_bug_4221():
    s = store.complete(make().id)
    assert s
```

Bug-id name. No assertion of the actual fix. Test passes for the wrong reason.

## Tooling Hints

- Python: `pytest -k`, `--pdb`, `--tb=short`, `breakpoint()`.
- Tracebacks: `RUST_BACKTRACE=full`, `JS --stack-trace-limit=200`, `--inspect-brk`.
- Logs: search by correlation id from the incident.

## Red Flags

- Fix lands without a failing test first.
- Test name encodes the bug number, not the behavior.
- "Works on my machine" closes the ticket.
- Symptom silenced with `try/except: pass` or default value.
- No `@regression` marker; future engineer cannot tell what is structural vs incidental.
