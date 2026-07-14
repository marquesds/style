---
id: tdd
kind: command
title: Run a TDD cycle
description: "Drive the next change RED → GREEN → REFACTOR. Test fails first."
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

Use skill:tdd.

Steps:

1. State and classify behavior Added/Removed/Changed/Unchanged.
2. For this cycle, follow skill:spec-driven-development's Behavioral Modeling
   Protocol with `workflow=tdd`; create/execute a fresh model or record fallback.
3. Write a failing test from accepted/forbidden traces. Run suite. Confirm RED.
4. Write minimum implementation. Run suite. Confirm GREEN.
5. Refactor. Tests stay green. No new behavior.
6. Repeat from step 1 with a new invocation, or finish.

For each cycle, output the failing test diff, the implementation diff, and the suite output proving GREEN.

If the test passes on the first run, stop. The test is wrong or already covered.
