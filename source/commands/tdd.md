---
id: tdd
kind: command
title: Run a TDD cycle
description: >
  Drive the next change RED → GREEN → REFACTOR. Test fails first.
agents:
  claude: { kind: command }
  cursor: { kind: command }
  codex:  { section: commands }
  vibe:   { kind: command }
---

Engage skill:tdd.

Steps:

1. State the behavior to add or change in one sentence.
2. Write a failing test that pins exactly that behavior. Run the suite. Confirm RED with the actual error.
3. Write the minimum implementation to pass. Run the suite. Confirm GREEN.
4. Refactor. Tests stay green. No new behavior.
5. Repeat for the next behavior, or finish.

Output per cycle: the failing test diff, the implementation diff, the suite output proving GREEN.

If the test passes on the first run, stop. The test is wrong or already covered.
