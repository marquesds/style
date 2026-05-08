---
id: plan
kind: command
title: Force plan mode
description: >
  Switch to plan mode. Map the change surface before any edit.
agents:
  claude: { kind: command }
  cursor: { kind: command }
  codex:  { section: commands }
  vibe:   { kind: command }
---

Engage rule:agent-workflow.

Steps:

1. Switch to plan mode. No edits, no shell side effects.
2. Identify modules, ports, and types that change.
3. List risks, open questions, and trade-offs.
4. Propose ordered tasks (each independently testable).
5. Output the plan and stop. Wait for human approval.

Hard limits:

- No file edits during this command.
- No commits, no pushes, no migrations.
- If exploration needs more than 3 files, spawn an explore subagent (rule:subagent-first).
