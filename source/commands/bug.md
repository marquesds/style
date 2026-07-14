---
id: bug
kind: command
title: Bug-first reproduction
description: "Reproduce the bug as a failing test before any fix. Stop the line until reproduction is locked in."
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

Use skill:bug-first-debugging.

Steps:

1. Stop adding features. Preserve the error output, logs, and repro steps verbatim.
2. Write a failing test that reproduces the bug. Tag `@regression`. The name should describe expected behavior, not the bug ID.
3. Run the suite. Confirm the test fails for the same reason the bug does.
4. Find the root cause. Ask "why?" until the answer is structural, not "this random null".
5. Fix the root cause. Re-run the suite. Test passes.
6. Run lint + types + the rest of the suite. Confirm no regressions elsewhere.
7. Commit with `fix(<scope>): <behavior restored>`. Reference the incident in the body, not the test name.

If the bug cannot be reproduced, stop and report. Do not guess a fix.
