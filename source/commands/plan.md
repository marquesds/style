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
  openclaw: { section: commands }
  opencode: { kind: command }
  pi:       { section: commands }
  vibe:   { kind: command }
---

Engage rule:agent-workflow.

Steps:

1. Switch to plan mode. No edits, no shell side effects.
2. Identify modules, ports, and types that change.
3. List risks, trade-offs, and **open questions**. Include the **Staff+/owner lens** from **rule:agent-workflow** (**Planning: Product + Requirements**): explicit gain/pain trade-offs (not risks-only) and owner-grade questions (cost of being wrong, cost of delay, reversibility, spend/SLA, who eats failure—see that rule for example prompts). If user-facing, cross-team, compliance, or vague/high-impact: also include **product-relevant open questions** (who affected, success metric, rollout, UX copy, edge users, compliance).
4. If requirement still fuzzy or blast radius large → point at **skill:requirements-crushing**; get **`Ready-to-Code: YES`** (or recorded human override) **before** ordered tasks.
5. Propose ordered tasks (each independently testable).
6. Output the plan and stop. Wait for human approval.

Hard limits:

- No file edits during this command.
- No commits, no pushes, no migrations.
- If exploration needs more than 3 files, spawn an explore subagent (rule:subagent-first).
