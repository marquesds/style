---
id: refactor
kind: command
title: Run a refactor cycle
description: "Apply one named structural transformation. Suite green before and after. Never mix refactor with feature work. Use skill:refactoring."
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

Use skill:refactoring.

Steps:

1. Confirm test suite is green BEFORE any change. If red, stop and report.
2. Name the transformation: Extract Function, Inline Variable, Move Method,
   Replace Conditional with Polymorphism, Introduce Parameter Object, etc.
3. Apply ONE transformation. Run the full suite. If it is green, continue. If it is red, revert.
4. Commit the refactor as a standalone commit (no feature work mixed in).
5. Repeat from step 2 for the next transformation, or declare done.

Constraints:

- Two hats: never add behavior during a refactor step.
- If behavior must change, finish the refactor commit first, then open a separate
  feature commit.
- If no tests cover the code under refactor, write characterization tests first
  (skill:refactoring legacy-code path).
