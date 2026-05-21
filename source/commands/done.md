---
id: done
kind: command
title: Walk Definition of Done
description: >
  Run the Definition-of-Done checklist on the current change before pushing
  or marking complete.
agents:
  claude: { kind: command }
  cursor: { kind: command }
  codex:  { section: commands }
  goose:  { section: commands }
  openclaw: { section: commands }
  opencode: { kind: command }
  pi:       { section: commands }
  vibe:   { kind: command }
---

Engage skill:definition-of-done.

Steps:

1. Run the full test suite. Report exact pass/fail counts.
2. Manually exercise every changed user/operator-visible surface: happy path plus relevant failure/edge. Record exact steps + observed result in final response and PR test plan.
3. Run the linter on changed files. Zero warnings.
4. Run the type checker. No new ignores.
5. Confirm new code is covered. Untested branches are intentional, not laziness.
6. Confirm new state changes have logs, new boundary calls have spans, new error paths have metrics.
7. Confirm perf budget: no new N+1, no blocking call in async path, no unbounded loop.
8. Self-walk the five axes (skill:code-review-and-quality).
9. Confirm docs updated for any user-facing surface change. ADR added if architectural.
10. Confirm commit messages follow Conventional Commits. PR template filled (skill:pull-request-and-commit-style).
11. Confirm risky / cross-team changes are behind a flag with a removal date.

Output: a green/red checklist. If anything is red, do NOT mark complete.
