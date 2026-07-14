---
id: definition-of-done
kind: skill
title: Definition of Done
description: "Tests + changed-surface manual proof + lint + types + coverage + observability + perf budget + 5-axis review. Walk before pushing or marking task complete."
applies_when:
  - about to push
  - about to mark a task complete
  - about to open a PR
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

# Definition of Done

Walk every step. Do not rely on "looks done". Done means proven done.

## Checklist

| Step | Pass means |
|---|---|
| Tests | Full suite green. New behavior pinned by tests. Bug fix has a regression test (skill:bug-first-debugging). |
| Changed-surface manual proof | Manually exercised every changed user/operator-visible surface in a real flow (staging, local parity, or documented env): happy path plus relevant failure/edge. **Record exact steps + observed result** in final response and PR test plan. Missing record = red. |
| Lint | Linter clean on changed files. Zero warnings. |
| Types | Static type check clean. No new `# type: ignore` / `as any` / `unwrap`. |
| Coverage | New code covered. Untested paths are intentional, not laziness. |
| Observability | New state changes log structured events. New boundary calls have spans. New error paths emit metrics (skill: observability rule). |
| Perf budget | No new N+1 (skill:n-plus-one-prevention). No unbounded loops or allocations. No blocking call in async path. |
| 5-axis review | Self-walked: correctness, readability, architecture, security, performance (skill:code-review-and-quality). |
| Docs | User-facing surface change documented. ADR added if architectural. |
| Commit + PR | Conventional Commits. Atomic. Test plan filled (skill:pull-request-and-commit-style). |
| Feature flag | Risky / partial → behind a flag with removal date. |

## Bash One-Liner

```bash
ruff check . && pyright && pytest -q && pytest --cov=src --cov-fail-under=85
```

Substitute idiomatic equivalents per language (`cargo test && cargo clippy -- -D warnings`, `mix test && mix dialyzer`, `pnpm test && pnpm tsc --noEmit`). Changed-surface manual proof is separate — not replaced by this one-liner.

## AGENTS.md Checklists

If the repo has `AGENTS.md` checklists (skill:agents-md-checklists), run the
"Before Opening a PR" checklist in full before marking done.

## "Would Staff Engineer Approve?"

Read your own diff as if reviewing it. Anything you'd flag → fix before pushing.

## GOOD

```text
DOD walk for #4231 (idempotent reset):
✓ pytest -q (84 passed, 0 failed)
✓ pyright clean
✓ ruff clean
✓ regression test test_reset_preserves_audit_log present
✓ manual proof: POST /sessions/{id}/reset ×2 idempotent; 404 path
✓ span "session.reset" added; counter sessions_reset_total
✓ no N+1 (1 select + 2 inserts)
✓ ADR-0007 added (idempotency key strategy)
✓ feat(sessions): idempotent reset endpoint
```

## BAD

```text
"all good, pushed"
```

No evidence. No proof. Reviewer is now QA.

## Red Flags

- Marking complete without running the suite end to end.
- Coverage drop accepted with "we'll add tests later".
- New endpoint shipped with no log + no span + no metric.
- "Refactor only, no tests needed" — refactors break things.
- Self-review skipped because "I wrote it, I trust it".
- UI, integration, auth, or operator-facing change with automated-only proof and no recorded manual replay.
