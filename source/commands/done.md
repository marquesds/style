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
2. Run the linter on changed files. Zero warnings.
3. Run the type checker. No new ignores.
4. Confirm new code is covered. Untested branches are intentional, not laziness.
5. Confirm new state changes have logs, new boundary calls have spans, new error paths have metrics.
6. Confirm perf budget: no new N+1, no blocking call in async path, no unbounded loop.
7. Self-walk the five axes (skill:code-review-and-quality).
8. Confirm docs updated for any user-facing surface change. ADR added if architectural.
9. Confirm commit messages follow Conventional Commits. PR template filled (skill:pull-request-and-commit-style).
10. Confirm risky / cross-team changes are behind a flag with a removal date.

Output: a green/red checklist. If anything is red, do NOT mark complete.
