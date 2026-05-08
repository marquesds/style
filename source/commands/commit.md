---
id: commit
kind: command
title: Generate Conventional Commit
description: >
  Generate a Conventional Commit message for staged changes. Subject in imperative mood,
  body explains why, footer references issues.
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

Engage skill:pull-request-and-commit-style.

Steps:

1. Inspect staged changes. If nothing is staged, stop and tell the user.
2. Identify the single logical change. If two unrelated changes, tell the user to split first.
3. Pick the type: `feat`, `fix`, `refactor`, `perf`, `test`, `docs`, `chore`, `build`, `ci`, `revert`.
4. Pick a scope from the changed paths (e.g. directory, module).
5. Write subject: imperative, ≤ 50 chars, no trailing period.
6. Write body: **why**, not what. Reference trade-offs or constraints if non-obvious.
7. Footer: `Closes <issue>`, `Refs <ticket>`, or `BREAKING CHANGE:` if applicable.

Output the message inside a code block. Do not run `git commit` automatically — print it for the user to confirm.
